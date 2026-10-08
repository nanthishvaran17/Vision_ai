import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.deps import get_db, get_current_user
from app.models.models import User, Conversation, Message, ImageRecord, VisualObject, VisualEvidence, VerificationRun, Claim, OCRResult, ConversationContext
from app.schemas.schemas import MessageCreate, MessageResponse, WhyThisAnswerPayload
from app.vision.verification_engine import verification_engine
from app.vision.memory import conversation_memory
from app.vision.question_generator import generate_dynamic_image_questions
from app.storage import get_storage_provider
from app.api.v1.ws import manager


router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("", response_model=MessageResponse)
async def send_message(
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify conversation ownership
    conv_stmt = select(Conversation).where(Conversation.id == msg_in.conversation_id, Conversation.user_id == current_user.id)
    conv_res = await db.execute(conv_stmt)
    conv = conv_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Broadcast websocket event: analysis_started
    await manager.broadcast_to_conversation(
        msg_in.conversation_id,
        "analysis_started",
        {"message": "Initiating visual reasoning pipeline", "question": msg_in.content}
    )

    # 1. Save User Message
    user_msg = Message(
        conversation_id=msg_in.conversation_id,
        role="user",
        content=msg_in.content,
        message_type=msg_in.message_type
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # 2. Retrieve referenced image in conversation
    target_image = None
    if msg_in.image_id:
        img_stmt = select(ImageRecord).where(ImageRecord.id == msg_in.image_id)
        img_res = await db.execute(img_stmt)
        target_image = img_res.scalar_one_or_none()
    else:
        # Get latest image uploaded in conversation
        img_stmt = select(ImageRecord).where(ImageRecord.conversation_id == msg_in.conversation_id).order_by(ImageRecord.created_at.desc())
        img_res = await db.execute(img_stmt)
        target_image = img_res.scalars().first()

    if not target_image:
        # Text-only response if no image available in conversation
        ai_msg = Message(
            conversation_id=msg_in.conversation_id,
            role="assistant",
            content="Please upload an image first so I can perform visual verification and answer your question.",
            message_type="AI_RESPONSE"
        )
        db.add(ai_msg)
        await db.commit()
        await db.refresh(ai_msg)
        return MessageResponse.model_validate(ai_msg)

    # Read image file bytes
    storage = get_storage_provider()
    image_bytes = await storage.get_file(target_image.file_path)

    # Get recent conversation memory / visual objects
    obj_stmt = select(VisualObject).where(VisualObject.image_id == target_image.id)
    obj_res = await db.execute(obj_stmt)
    existing_objects = [
        {
            "id": o.id, "label": o.label, "confidence": o.confidence,
            "box": {"x1": o.x1, "y1": o.y1, "x2": o.x2, "y2": o.y2},
            "attributes": json.loads(o.attributes_json) if o.attributes_json else {}
        }
        for o in obj_res.scalars().all()
    ]

    # Fetch existing OCR results from DB if available
    ocr_stmt = select(OCRResult).where(OCRResult.image_id == target_image.id)
    ocr_res = await db.execute(ocr_stmt)
    existing_ocr_rows = ocr_res.scalars().all()
    existing_ocr = None
    if existing_ocr_rows:
        combined_text = " ".join(r.text for r in existing_ocr_rows)
        all_items = []
        for r in existing_ocr_rows:
            if r.bounding_boxes_json:
                try:
                    all_items.extend(json.loads(r.bounding_boxes_json))
                except Exception:
                    pass
        existing_ocr = {
            "text": combined_text,
            "items": all_items,
            "entities": ocr_engine._extract_entities(combined_text),
            "has_text": bool(combined_text.strip()),
            "word_count": len(combined_text.split())
        }

    # Resolve Pronouns ("it", "this", "that") via memory
    memory_res = conversation_memory.resolve_pronouns(msg_in.content, existing_objects)
    question_to_engine = memory_res["augmented_query"]

    # Defined WebSocket callback for progress streaming
    async def ws_step_callback(event_type: str, message: str, data: dict):
        await manager.broadcast_to_conversation(
            msg_in.conversation_id,
            event_type,
            {"description": message, "step_info": data}
        )

    # 3. Execute Active Visual Verification Pipeline
    verif_res = await verification_engine.run_verification_pipeline(
        image_bytes=image_bytes,
        question=question_to_engine,
        recent_objects=existing_objects,
        is_challenge_mode=msg_in.is_challenge,
        ws_callback=ws_step_callback,
        existing_ocr=existing_ocr
    )

    # Save visual objects to DB if not saved yet
    for obj in verif_res.get("objects", []):
        existing_obj_db = next((o for o in existing_objects if o["id"] == obj["id"]), None)
        if not existing_obj_db:
            vo = VisualObject(
                image_id=target_image.id,
                label=obj["label"],
                confidence=obj["confidence"],
                x1=obj["box"]["x1"],
                y1=obj["box"]["y1"],
                x2=obj["box"]["x2"],
                y2=obj["box"]["y2"],
                attributes_json=json.dumps(obj.get("attributes", {}))
            )
            db.add(vo)

    # Save OCR Result if present
    ocr_data = verif_res.get("ocr_data", {})
    if ocr_data.get("has_text"):
        ocr_row = OCRResult(
            image_id=target_image.id,
            text=ocr_data["text"],
            bounding_boxes_json=json.dumps(ocr_data.get("items", [])),
            confidence=0.9
        )
        db.add(ocr_row)

    # Save Verification Run
    vrun = VerificationRun(
        image_id=target_image.id,
        message_id=user_msg.id,
        question=msg_in.content,
        initial_answer=verif_res["answer"],
        initial_confidence=verif_res["initial_confidence"],
        verification_required=verif_res["verification_required"],
        verification_steps_json=json.dumps(verif_res["verification_steps"]),
        final_confidence=verif_res["final_confidence"],
        status="COMPLETED"
    )
    db.add(vrun)
    await db.commit()

    # Formulate "Why this answer" payload & dynamic questions
    dyn_gen = generate_dynamic_image_questions(
        verif_res.get("objects", []),
        verif_res.get("ocr_data", {}),
        verif_res.get("scene"),
        verif_res.get("spatial_relations")
    )

    why_payload = WhyThisAnswerPayload(
        question=msg_in.content,
        answer=verif_res["answer"],
        confidence=verif_res["final_confidence"],
        evidence_level=verif_res["final_confidence"],
        evidence=verif_res["evidence"],
        verification_steps=verif_res["verification_steps"],
        unsupported_claims=verif_res["unsupported_claims"],
        annotations=[
            {
                "id": o["id"],
                "label": o["label"],
                "confidence": o["confidence"],
                "box": o["box"],
                "attributes": o.get("attributes", {})
            }
            for o in verif_res.get("objects", [])
        ],
        suggested_questions=dyn_gen["suggested_questions"]
    )


    # 4. Save AI Response Message
    ai_msg = Message(
        conversation_id=msg_in.conversation_id,
        role="assistant",
        content=verif_res["answer"],
        message_type="AI_RESPONSE",
        metadata_json=why_payload.model_dump_json()
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    # Broadcast answer_ready
    await manager.broadcast_to_conversation(
        msg_in.conversation_id,
        "answer_ready",
        {"message_id": ai_msg.id, "answer": ai_msg.content, "why_this_answer": why_payload.model_dump()}
    )

    resp = MessageResponse.model_validate(ai_msg)
    resp.why_this_answer = why_payload
    return resp
