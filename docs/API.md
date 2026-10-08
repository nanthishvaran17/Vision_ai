# VisionNext AI — API Documentation

All API endpoints are prefixed with `/api/v1`.

## Auth Endpoints
- `POST /api/v1/auth/register` — Register new user account.
- `POST /api/v1/auth/login` — Authenticate user and receive access + refresh JWTs.
- `POST /api/v1/auth/refresh` — Refresh expired access token.
- `GET /api/v1/auth/me` — Get current user profile.

## Conversation Endpoints
- `GET /api/v1/conversations` — List active user conversations.
- `POST /api/v1/conversations` — Create new conversation.
- `GET /api/v1/conversations/{id}` — Fetch conversation with full message history.
- `DELETE /api/v1/conversations/{id}` — Delete conversation and associated evidence.

## Message Endpoints
- `POST /api/v1/messages` — Send user prompt, trigger visual verification engine, and receive grounded response.

## Image Endpoints
- `POST /api/v1/images/upload` — Upload image file (multipart), run magic byte check, resize, and perform object & OCR detection.
- `GET /api/v1/images/{id}/objects` — Fetch detected visual object bounding boxes.
- `GET /api/v1/images/{id}/ocr` — Fetch extracted OCR text items.

## Vision Endpoints
- `POST /api/v1/vision/compare` — Compare Image A vs Image B for structural visual differences.

## Health Endpoints
- `GET /api/v1/health` — System operational status and component health.
- `GET /api/v1/health/database` — Database connection check.
- `GET /api/v1/health/ai` — AI provider status check.

## WebSocket
- `WS /api/v1/ws/conversations/{conversation_id}?token={JWT_ACCESS_TOKEN}` — Stream live verification steps (`analysis_started`, `verification_step_completed`, `answer_ready`).
