import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.deps import get_db
from app.config import settings
from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["Health"])

start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    ai_status = "healthy" if settings.LLM_PROVIDER in ["openai", "ollama"] else "degraded"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        ai_provider=f"{settings.LLM_PROVIDER} ({ai_status})",
        ocr_engine=settings.OCR_PROVIDER,
        version=settings.VERSION,
        uptime_seconds=round(time.time() - start_time, 2)
    )

@router.get("/health/database")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health/ai")
async def ai_health_check():
    return {
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
        "vision_model": settings.VISION_MODEL,
        "ocr_provider": settings.OCR_PROVIDER,
        "status": "healthy"
    }
