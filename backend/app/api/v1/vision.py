from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, get_current_user
from app.models.models import User, ImageRecord
from app.schemas.schemas import ImageComparisonRequest, ImageComparisonResponse
from app.storage import get_storage_provider
from app.vision.verification_engine import verification_engine
from app.vision.comparator import image_comparator

router = APIRouter(prefix="/vision", tags=["Vision"])

@router.post("/compare", response_model=ImageComparisonResponse)
async def compare_images_endpoint(
    req: ImageComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_a = select(ImageRecord).where(ImageRecord.id == req.image_a_id)
    stmt_b = select(ImageRecord).where(ImageRecord.id == req.image_b_id)

    res_a = await db.execute(stmt_a)
    res_b = await db.execute(stmt_b)

    img_a = res_a.scalar_one_or_none()
    img_b = res_b.scalar_one_or_none()

    if not img_a or not img_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both images not found")

    storage = get_storage_provider()
    bytes_a = await storage.get_file(img_a.file_path)
    bytes_b = await storage.get_file(img_b.file_path)

    comp_res = image_comparator.compare_images(bytes_a, bytes_b)

    return ImageComparisonResponse(
        id=f"comp_{img_a.id[:8]}_{img_b.id[:8]}",
        image_a_id=req.image_a_id,
        image_b_id=req.image_b_id,
        added_objects=comp_res["added_objects"],
        removed_objects=comp_res["removed_objects"],
        moved_objects=comp_res["moved_objects"],
        changed_text=comp_res["changed_text"],
        summary=comp_res["summary"]
    )
