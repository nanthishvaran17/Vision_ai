import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, get_current_user
from app.models.models import User, VerificationRun

router = APIRouter(prefix="/verification", tags=["Verification"])

@router.get("/{verification_id}")
async def get_verification_run(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(VerificationRun).where(VerificationRun.id == verification_id)
    res = await db.execute(stmt)
    vrun = res.scalar_one_or_none()
    if not vrun:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification run not found")

    return {
        "id": vrun.id,
        "image_id": vrun.image_id,
        "question": vrun.question,
        "initial_answer": vrun.initial_answer,
        "initial_confidence": vrun.initial_confidence,
        "final_confidence": vrun.final_confidence,
        "verification_required": vrun.verification_required,
        "verification_steps": json.loads(vrun.verification_steps_json) if vrun.verification_steps_json else [],
        "status": vrun.status,
        "created_at": vrun.created_at
    }
