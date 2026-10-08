import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.logging import setup_logging, logger
from app.deps import engine
from app.models.models import Base
from app.security.rate_limit import limiter
from app.api.v1 import auth, conversations, messages, images, vision, verification, health, ws

setup_logging()

# Ensure upload directories exist at module initialization time for StaticFiles mounting
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "thumbnails"), exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("application_started", version=settings.VERSION)
    yield
    # Shutdown
    await engine.dispose()
    logger.info("application_stopped")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Error Handler (Section 9: No raw stack traces exposed to users)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Static file serving for uploaded images & thumbnails
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers under /api/v1
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_prefix)
app.include_router(conversations.router, prefix=api_prefix)
app.include_router(messages.router, prefix=api_prefix)
app.include_router(images.router, prefix=api_prefix)
app.include_router(vision.router, prefix=api_prefix)
app.include_router(verification.router, prefix=api_prefix)
app.include_router(health.router, prefix=api_prefix)
app.include_router(ws.router, prefix=api_prefix)

@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "tagline": "Don't Just See. Verify.",
        "version": settings.VERSION,
        "docs": "/docs"
    }
