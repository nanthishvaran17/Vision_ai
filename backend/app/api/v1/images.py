import uuid
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, get_current_user
from app.models.models import User, Conversation, ImageRecord, VisualObject, OCRResult, VisualEvidence
from app.schemas.schemas import ImageUploadResponse
from app.security.upload_guard import validate_and_preprocess_image
from app.storage import get_storage_provider
from app.vision.object_detector import object_detector
from app.vision.ocr import ocr_engine
from app.vision.scene_analyzer import scene_analyzer
from app.vision.spatial_analyzer import spatial_analyzer
from app.vision.question_generator import generate_dynamic_image_questions

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify conversation ownership or auto-create if missing/invalid/temp
    conv = None
    if conversation_id and conversation_id != "temp":
        conv_stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        conv_res = await db.execute(conv_stmt)
        conv = conv_res.scalar_one_or_none()

    if not conv:
        conv = Conversation(
            user_id=current_user.id,
            title="Image Upload Session"
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

    target_conv_id = conv.id
    content = await file.read()
    
    # 1. Security & MIME validation + EXIF rotation + SHA256 + resize
    prep_data = validate_and_preprocess_image(content)
    sha256 = prep_data["sha256"]

    storage = get_storage_provider()
    ext = prep_data["format"].lower()
    filename = f"{sha256[:16]}_{uuid.uuid4().hex[:8]}.{ext}"
    thumb_filename = f"thumb_{sha256[:16]}_{uuid.uuid4().hex[:8]}.{ext}"

    # Save clean image and thumbnail
    rel_file_path = await storage.save_file(prep_data["content"], filename, subfolder="images")
    rel_thumb_path = await storage.save_file(prep_data["thumbnail_content"], thumb_filename, subfolder="thumbnails")

    # 2. Check SHA-256 cache for existing image detections
    cached_img_stmt = select(ImageRecord).where(ImageRecord.sha256 == sha256).limit(1)
    cached_res = await db.execute(cached_img_stmt)
    cached_img = cached_res.scalar_one_or_none()

    img_record = ImageRecord(
        conversation_id=target_conv_id,
        file_path=rel_file_path,
        thumbnail_path=rel_thumb_path,
        sha256=sha256,
        width=prep_data["width"],
        height=prep_data["height"],
        mime_type=prep_data["mime_type"]
    )
    db.add(img_record)
    await db.commit()
    await db.refresh(img_record)

    # 3. Detect objects & text (reuse cache or run computer vision)
    formatted_objs = []
    ocr_data = {"has_text": False, "text": "", "items": []}

    if cached_img:
        cached_objs_stmt = select(VisualObject).where(VisualObject.image_id == cached_img.id)
        c_objs = (await db.execute(cached_objs_stmt)).scalars().all()
        for co in c_objs:
            db.add(VisualObject(
                image_id=img_record.id, label=co.label, confidence=co.confidence,
                x1=co.x1, y1=co.y1, x2=co.x2, y2=co.y2, attributes_json=co.attributes_json
            ))
            attrs = json.loads(co.attributes_json) if co.attributes_json else {}
            formatted_objs.append({
                "id": co.id, "label": co.label, "confidence": co.confidence,
                "box": {"x1": co.x1, "y1": co.y1, "x2": co.x2, "y2": co.y2},
                "attributes": attrs
            })

        cached_ocr_stmt = select(OCRResult).where(OCRResult.image_id == cached_img.id)
        c_ocr = (await db.execute(cached_ocr_stmt)).scalars().all()
        for ro in c_ocr:
            db.add(OCRResult(
                image_id=img_record.id, text=ro.text, bounding_boxes_json=ro.bounding_boxes_json,
                confidence=ro.confidence, language=ro.language
            ))
        await db.commit()

        obj_count = len(c_objs)
        combined_text = " ".join(ro.text for ro in c_ocr)
        text_len = len(combined_text)
        ocr_data = {"has_text": bool(combined_text.strip()), "text": combined_text, "items": []}
    else:
        detected_objs = object_detector.detect_objects(prep_data["content"])
        for obj in detected_objs:
            vo = VisualObject(
                image_id=img_record.id, label=obj["label"], confidence=obj["confidence"],
                x1=obj["box"]["x1"], y1=obj["box"]["y1"], x2=obj["box"]["x2"], y2=obj["box"]["y2"],
                attributes_json=json.dumps(obj.get("attributes", {}))
            )
            db.add(vo)
            formatted_objs.append(obj)

        ocr_data = ocr_engine.extract_text(prep_data["content"])
        if ocr_data.get("has_text"):
            db.add(OCRResult(
                image_id=img_record.id, text=ocr_data["text"],
                bounding_boxes_json=json.dumps(ocr_data.get("items", [])), confidence=0.9
            ))
        await db.commit()

        obj_count = len(detected_objs)
        text_len = len(ocr_data.get("text", ""))

    # 4. Generate dynamic image questions
    scene_info = scene_analyzer.analyze_scene(prep_data["content"])
    spatial_rels = spatial_analyzer.analyze_spatial_relations(formatted_objs)
    dyn_gen = generate_dynamic_image_questions(formatted_objs, ocr_data, scene_info, spatial_rels)

    # 5. Smart auto-title conversation if title is default or generic
    if conv and (not conv.title or conv.title in ["New Verification Chat", "Visual Verification Session", "Image Upload Session"]):
        if ocr_data.get("has_text") and ocr_data.get("text"):
            clean_t = ocr_data["text"].split("\n")[0][:25].strip()
            if clean_t and "Text region" not in clean_t:
                conv.title = f"Doc: {clean_t}"
        if conv.title in ["New Verification Chat", "Visual Verification Session", "Image Upload Session"]:
            if formatted_objs:
                top_labels = list(dict.fromkeys(o["label"] for o in formatted_objs[:2]))
                conv.title = f"{' & '.join(top_labels).title()} Scan"
            else:
                conv.title = "Visual Scan Session"
        await db.commit()

    return ImageUploadResponse(

        id=img_record.id,
        conversation_id=target_conv_id,
        file_path=rel_file_path,
        thumbnail_path=rel_thumb_path,
        sha256=sha256,
        width=img_record.width,
        height=img_record.height,
        mime_type=img_record.mime_type,
        objects_count=obj_count,
        ocr_text_length=text_len,
        suggested_questions=dyn_gen["suggested_questions"],
        initial_summary=dyn_gen["initial_summary"]
    )


@router.get("/{image_id}/objects")
async def get_image_objects(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(VisualObject).where(VisualObject.image_id == image_id)
    res = await db.execute(stmt)
    objs = res.scalars().all()
    return [
        {
            "id": o.id, "label": o.label, "confidence": o.confidence,
            "box": {"x1": o.x1, "y1": o.y1, "x2": o.x2, "y2": o.y2},
            "attributes": json.loads(o.attributes_json) if o.attributes_json else {}
        }
        for o in objs
    ]

@router.get("/{image_id}/ocr")
async def get_image_ocr(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(OCRResult).where(OCRResult.image_id == image_id)
    res = await db.execute(stmt)
    ocrs = res.scalars().all()
    return [
        {
            "id": o.id, "text": o.text, "confidence": o.confidence,
            "bounding_boxes": json.loads(o.bounding_boxes_json) if o.bounding_boxes_json else []
        }
        for o in ocrs
    ]

@router.get("/{image_id}/dynamic-questions")
async def get_image_dynamic_questions(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ImageRecord).where(ImageRecord.id == image_id)
    res = await db.execute(stmt)
    img = res.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    storage = get_storage_provider()
    image_bytes = await storage.get_file(img.file_path)

    objs_stmt = select(VisualObject).where(VisualObject.image_id == image_id)
    objs_res = await db.execute(objs_stmt)
    formatted_objs = [
        {
            "id": o.id, "label": o.label, "confidence": o.confidence,
            "box": {"x1": o.x1, "y1": o.y1, "x2": o.x2, "y2": o.y2},
            "attributes": json.loads(o.attributes_json) if o.attributes_json else {}
        }
        for o in objs_res.scalars().all()
    ]

    ocr_stmt = select(OCRResult).where(OCRResult.image_id == image_id)
    ocr_rows = (await db.execute(ocr_stmt)).scalars().all()
    combined_text = " ".join(r.text for r in ocr_rows)
    ocr_data = {
        "has_text": bool(combined_text.strip()),
        "text": combined_text,
        "items": [],
        "entities": ocr_engine._extract_entities(combined_text)
    }

    scene_info = scene_analyzer.analyze_scene(image_bytes)
    spatial_rels = spatial_analyzer.analyze_spatial_relations(formatted_objs)
    dyn_res = generate_dynamic_image_questions(formatted_objs, ocr_data, scene_info, spatial_rels)
    return dyn_res

