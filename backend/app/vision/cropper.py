import io
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Dict, Any

def crop_and_zoom_region(image_bytes: bytes, box: Dict[str, float], zoom_factor: float = 1.5, contrast_factor: float = 1.3) -> bytes:
    """
    Crops specified normalized region [x1, y1, x2, y2] from image, applies zoom expansion and contrast enhancement.
    Used during Active Verification steps (TARGET_CROP, TARGET_ZOOM, re-OCR).
    """
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = pil_img.size

    x1 = int(max(0.0, box.get("x1", 0.0)) * w)
    y1 = int(max(0.0, box.get("y1", 0.0)) * h)
    x2 = int(min(1.0, box.get("x2", 1.0)) * w)
    y2 = int(min(1.0, box.get("y2", 1.0)) * h)

    # Add margin padding for zoom
    box_w = x2 - x1
    box_h = y2 - y1
    pad_w = int((box_w * (zoom_factor - 1.0)) / 2.0)
    pad_h = int((box_h * (zoom_factor - 1.0)) / 2.0)

    crop_x1 = max(0, x1 - pad_w)
    crop_y1 = max(0, y1 - pad_h)
    crop_x2 = min(w, x2 + pad_w)
    crop_y2 = min(h, y2 + pad_h)

    cropped = pil_img.crop((crop_x1, crop_y1, crop_x2, crop_y2))

    # Apply contrast enhancement for fine text/logo reading
    enhancer = ImageEnhance.Contrast(cropped)
    enhanced = enhancer.enhance(contrast_factor)

    sharpener = ImageEnhance.Sharpness(enhanced)
    final_img = sharpener.enhance(1.4)

    buffer = io.BytesIO()
    final_img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()
