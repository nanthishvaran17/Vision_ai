# VisionNext AI — Environment & Setup Guide

## Requirements
- Python 3.12+
- Node.js v18+ & npm
- SQLite / PostgreSQL

## Backend Environment Setup (`.env`)
```ini
DATABASE_URL=sqlite+aiosqlite:///./visionnext.db
JWT_SECRET=super-secret-visionnext-jwt-key-2026-codienych-secure
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OCR_PROVIDER=easyocr
STORAGE_PROVIDER=local
UPLOAD_DIR=./uploads
```

## Launching Services

```bash
# Terminal 1: Backend API
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend Client
cd frontend
npm run dev
```
