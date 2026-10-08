# VisionNext AI — System Architecture

## Architecture Overview

VisionNext AI utilizes a decoupled client-server architecture designed for real-time visual reasoning and high-precision active verification.

```
[ Frontend: React + TypeScript + Vite + Tailwind CSS ]
                       │
       HTTP REST API & WebSocket Streaming
                       │
   [ Backend API Gateway: FastAPI + Uvicorn ]
                       │
  ┌────────────────────┴────────────────────┐
  ▼                                         ▼
[ Security & Auth Guard ]         [ Storage Abstraction ]
  - Argon2 Password Hash            - Local Filesystem
  - JWT Rotation                    - S3 Compatible
  - Magic Byte MIME Check
  - Decompression Bomb Guard
                       │
                       ▼
      [ Active Visual Verification Engine ]
  ┌────────────────────┼────────────────────┐
  ▼                    ▼                    ▼
[ Object Detector ]  [ OCR Engine ]   [ Spatial Geometry ]
  - OpenCV Feature     - EasyOCR /      - Normalized Matrix
  - Bounding Boxes      Tesseract       - Relational Solver
                       │
                       ▼
       [ Evidence Fusion & Claim Validator ]
         - Qualitative Evidence Levels
         - Hallucination Rejection Guard
                       │
                       ▼
        [ Multimodal Model Router ]
         - OpenAI / Ollama / Engine Fallback
```

## Core Subsystems

### 1. Visual Verification State Machine
```
INITIAL_ANALYSIS ──> UNCERTAINTY_DETECTED ──> TARGET_IDENTIFICATION
                             │
                             ▼
  FINAL_RESPONSE <── CLAIM_VALIDATION <── EVIDENCE_FUSION <── TARGET_CROP & ZOOM
```

### 2. Grounding Overlay Engine
Maps normalized bounding box coordinates `[x1, y1, x2, y2]` (scale 0.0 to 1.0) onto responsive image elements via SVG overlay paths.
