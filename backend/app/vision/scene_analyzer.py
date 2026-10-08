import cv2
import numpy as np
import io
from typing import Dict, Any
from PIL import Image

class SceneAnalyzer:
    def analyze_scene(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyzes scene characteristics from image pixel array:
        brightness, contrast, orientation, aspect ratio, dominant colors, and texture density.
        """
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)
        h, w, _ = img_np.shape

        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Brightness (average pixel intensity 0-255)
        brightness = float(np.mean(gray))
        
        # Contrast (standard deviation of grayscale)
        contrast = float(np.std(gray))
        
        # Aspect Ratio & Orientation
        aspect_ratio = round(w / float(h), 2)
        orientation = "landscape" if w > h else ("portrait" if h > w else "square")

        # Texture / Laplacian Variance (sharpness vs blur)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_sharp = laplacian_var > 100.0

        # Dominant Colors via k-means clustering
        pixels = img_np.reshape(-1, 3).astype(np.float32)
        # Sample for speed if large
        if len(pixels) > 10000:
            indices = np.random.choice(len(pixels), 10000, replace=False)
            pixels = pixels[indices]
            
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        counts = np.bincount(labels.flatten())
        total_counts = sum(counts)
        
        dominant_colors = []
        for i in range(len(centers)):
            percent = round((counts[i] / total_counts) * 100, 1)
            color_rgb = [int(c) for c in centers[i]]
            dominant_colors.append({
                "rgb": color_rgb,
                "percentage": percent
            })

        dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)

        return {
            "width": w,
            "height": h,
            "brightness": round(brightness, 1),
            "brightness_level": "bright" if brightness > 170 else ("dark" if brightness < 85 else "normal"),
            "contrast": round(contrast, 1),
            "sharpness_score": round(laplacian_var, 1),
            "is_sharp": is_sharp,
            "aspect_ratio": aspect_ratio,
            "orientation": orientation,
            "dominant_colors": dominant_colors
        }

scene_analyzer = SceneAnalyzer()
