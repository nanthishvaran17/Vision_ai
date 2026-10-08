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
    if cached_img:
        cached_objs_stmt = select(VisualObject).where(VisualObject.image_id == cached_img.id)
        c_objs = (await db.execute(cached_objs_stmt)).scalars().all()
        for co in c_objs:
            db.add(VisualObject(
                image_id=img_record.id, label=co.label, confidence=co.confidence,
                x1=co.x1, y1=co.y1, x2=co.x2, y2=co.y2, attributes_json=co.attributes_json
            ))
        cached_ocr_stmt = select(OCRResult).where(OCRResult.image_id == cached_img.id)
        c_ocr = (await db.execute(cached_ocr_stmt)).scalars().all()
        for ro in c_ocr:
            db.add(OCRResult(
                image_id=img_record.id, text=ro.text, bounding_boxes_json=ro.bounding_boxes_json,
                confidence=ro.confidence, language=ro.language
            ))
        await db.commit()

        obj_count = len(c_objs)
        text_len = sum(len(ro.text) for ro in c_ocr)
    else:
        detected_objs = object_detector.detect_objects(prep_data["content"])
        for obj in detected_objs:
            vo = VisualObject(
                image_id=img_record.id, label=obj["label"], confidence=obj["confidence"],
                x1=obj["box"]["x1"], y1=obj["box"]["y1"], x2=obj["box"]["x2"], y2=obj["box"]["y2"],
                attributes_json=json.dumps(obj.get("attributes", {}))
            )
            db.add(vo)

        ocr_data = ocr_engine.extract_text(prep_data["content"])
        if ocr_data.get("has_text"):
            db.add(OCRResult(
                image_id=img_record.id, text=ocr_data["text"],
                bounding_boxes_json=json.dumps(ocr_data.get("items", [])), confidence=0.9
            ))
        await db.commit()

        obj_count = len(detected_objs)
        text_len = len(ocr_data.get("text", ""))

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
        ocr_text_length=text_len
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
