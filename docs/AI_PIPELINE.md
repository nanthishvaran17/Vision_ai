# VisionNext AI — Active Visual Verification Engine Pipeline

## Pipeline Execution Order

```
1. Image Upload & Magic Byte Verification
2. OpenCV / PyTorch Object Bounding Box Detection
3. OCR Text & Entity Extraction
4. Scene Analysis & Dominant Color Extraction
5. Deterministic Bounding Box Spatial Geometry Matrix
6. Initial Evidence Level Calculation (HIGH / MEDIUM / LOW / INSUFFICIENT)
7. Active Verification Routing (Crop -> Zoom -> Re-OCR -> Attribute Check)
8. Evidence Fusion Engine
9. Hallucination Guard (Claim Validator)
10. Final Response Generation & Visual Grounding Overlay
```

## Evidence Levels
- **HIGH**: Strong visual detection, clear OCR match, verified spatial alignment.
- **MEDIUM**: Clear object visual features, basic OCR or spatial relations.
- **LOW**: Ambiguous shapes, unreadable distant text, low confidence detections.
- **INSUFFICIENT**: High noise, missing visual features, unsupported claims.
