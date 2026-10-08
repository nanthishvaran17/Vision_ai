import hashlib
import io
from PIL import Image, ImageOps
from fastapi import HTTPException, status
from app.config import settings

# Enforce Decompression bomb protection limit
Image.MAX_IMAGE_PIXELS = 25_000_000

ALLOWED_MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WEBP starts with RIFF ... WEBP
}

def detect_mime_type(content: bytes) -> str:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif content.startswith(b"RIFF") and len(content) >= 12 and content[8:12] == b"WEBP":
        return "image/webp"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid image format. Only JPEG, PNG, and WEBP images are accepted."
    )

def validate_and_preprocess_image(content: bytes):
    # 1. Size check
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    # 2. Magic byte MIME check
    mime_type = detect_mime_type(content)

    # 3. Safe decode & Decompression bomb guard
    try:
        image = Image.open(io.BytesIO(content))
        image.load()  # Fast single-pass verification and pixel load
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or invalid image file: {str(e)}"
        )

    # 4. Fix EXIF orientation
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    # 5. Convert mode to RGB/RGBA
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    # 6. Compute SHA-256 hash
    sha256_hash = hashlib.sha256(content).hexdigest()

    # 7. Strip metadata using fast C-level canvas paste (eliminates memory-heavy getdata allocations)
    clean_img = Image.new(image.mode, image.size)
    clean_img.paste(image)

    # 8. Optimize dimensions (max 1920px) for ultra-fast CV & OCR processing without losing quality
    max_dim = 1920
    width, height = clean_img.size
    if width > max_dim or height > max_dim:
        clean_img.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)
        width, height = clean_img.size

    # Save cleaned image to bytes
    out_buffer = io.BytesIO()
    fmt = "JPEG" if mime_type == "image/jpeg" else ("PNG" if mime_type == "image/png" else "WEBP")
    clean_img.save(out_buffer, format=fmt, quality=90)
    clean_bytes = out_buffer.getvalue()

    # 9. Fast thumbnail generation (300x300 max)
    thumb_img = clean_img.copy()
    thumb_img.thumbnail((300, 300), Image.Resampling.BILINEAR)
    thumb_buffer = io.BytesIO()
    thumb_img.save(thumb_buffer, format=fmt, quality=75)
    thumb_bytes = thumb_buffer.getvalue()

    return {
        "content": clean_bytes,
        "thumbnail_content": thumb_bytes,
        "mime_type": mime_type,
        "width": width,
        "height": height,
        "sha256": sha256_hash,
        "format": fmt
    }
