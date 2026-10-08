from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "VisionNext AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./visionnext.db"
    
    JWT_SECRET: str = "super-secret-visionnext-jwt-key-2026-codienych-secure"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_MINUTES: int = 60
    JWT_REFRESH_DAYS: int = 7
    
    LLM_PROVIDER: str = "openai"  # openai | ollama
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    VISION_MODEL: str = "gpt-4o-mini"
    STRONG_MODEL: str = "gpt-4o"
    
    OCR_PROVIDER: str = "easyocr"  # easyocr | paddle | tesseract | opencv
    STORAGE_PROVIDER: str = "local"  # local | s3
    UPLOAD_DIR: str = "./uploads"
    
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    
    MAX_IMAGE_SIZE_MB: int = 10
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    CONFIDENCE_THRESHOLD_HIGH: float = 0.85
    CONFIDENCE_THRESHOLD_LOW: float = 0.45

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
