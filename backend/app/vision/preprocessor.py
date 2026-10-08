from PIL import Image
import numpy as np

def load_image_as_numpy(image_bytes: bytes) -> np.ndarray:
    import io
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(pil_image)

def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    import io
    pil_image = Image.open(io.BytesIO(image_bytes))
    return pil_image.width, pil_image.height
