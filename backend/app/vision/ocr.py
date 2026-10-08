import cv2
import numpy as np
import io
import re
from typing import List, Dict, Any
from PIL import Image

class OCREngine:
    def __init__(self):
        self._reader = None
        self._rapid_ocr = None

    def _get_rapid_ocr(self):
        if self._rapid_ocr is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._rapid_ocr = RapidOCR()
            except BaseException:
                self._rapid_ocr = False
        return self._rapid_ocr if self._rapid_ocr is not False else None

    def _get_easyocr_reader(self):
        if self._reader is None:
            try:
                import easyocr
                self._reader = easyocr.Reader(['en'], gpu=False)
            except BaseException:
                self._reader = False
        return self._reader if self._reader is not False else None

    def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts real text and bounding boxes from image pixels using OCR (RapidOCR / PyTesseract / EasyOCR).
        Returns parsed text, structured items, and extracted entities (dates, times, venues, URLs, numbers).
        """
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)
        h, w, _ = img_np.shape

        ocr_items: List[Dict[str, Any]] = []

        # 1. Try RapidOCR first (ONNX-native, fast, no DLL issues)
        rapid_engine = self._get_rapid_ocr()
        if rapid_engine is not None:
            try:
                results, _ = rapid_engine(image_bytes)
                if results:
                    for bbox, text, score in results:
                        prob = float(score)
                        if prob < 0.2 or not text.strip():
                            continue
                        pts = np.array(bbox)
                        x1 = round(float(np.min(pts[:, 0])) / w, 4)
                        y1 = round(float(np.min(pts[:, 1])) / h, 4)
                        x2 = round(float(np.max(pts[:, 0])) / w, 4)
                        y2 = round(float(np.max(pts[:, 2])) / h, 4) if len(pts) > 2 else round(float(np.max(pts[:, 1])) / h, 4)
                        
                        ocr_items.append({
                            "text": text.strip(),
                            "confidence": round(prob, 2),
                            "box": {"x1": max(0.0, x1), "y1": max(0.0, y1), "x2": min(1.0, x2), "y2": min(1.0, y2)}
                        })
            except BaseException:
                pass

        # 2. Try PyTesseract if RapidOCR yielded no items
        if not ocr_items:
            try:
                import pytesseract
                raw_txt = pytesseract.image_to_string(pil_img).strip()
                if raw_txt:
                    data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                    for i in range(len(data.get('text', []))):
                        txt = data['text'][i].strip()
                        conf = float(data['conf'][i])
                        if conf > 15 and len(txt) > 0:
                            x, y, bw, bh = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                            ocr_items.append({
                                "text": txt,
                                "confidence": round(max(0.4, conf / 100.0), 2),
                                "box": {
                                    "x1": round(x / w, 4),
                                    "y1": round(y / h, 4),
                                    "x2": round((x + bw) / w, 4),
                                    "y2": round((y + bh) / h, 4)
                                }
                            })
            except BaseException:
                pass

        # 3. Try EasyOCR if still no items
        if not ocr_items:
            reader = self._get_easyocr_reader()
            if reader is not None:
                try:
                    results = reader.readtext(img_np)
                    for bbox, text, prob in results:
                        if prob < 0.15 or not text.strip():
                            continue
                        pts = np.array(bbox)
                        x1 = round(float(np.min(pts[:, 0])) / w, 4)
                        y1 = round(float(np.min(pts[:, 1])) / h, 4)
                        x2 = round(float(np.max(pts[:, 0])) / w, 4)
                        y2 = round(float(np.max(pts[:, 2])) / h, 4) if len(pts) > 2 else round(float(np.max(pts[:, 1])) / h, 4)
                        
                        ocr_items.append({
                            "text": text.strip(),
                            "confidence": round(float(prob), 2),
                            "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                        })
                except BaseException:
                    pass

        # Fallback to OpenCV contour text region analysis if no OCR items returned
        if not ocr_items:
            ocr_items = self._opencv_text_region_fallback(img_np, w, h)

        real_words = [item["text"] for item in ocr_items if not item["text"].startswith("Text region at")]
        full_text = " ".join(real_words)
        entities = self._extract_entities(full_text)

        has_real_text = len(full_text.strip()) > 0

        return {
            "text": full_text if has_real_text else ("Text regions detected" if ocr_items else ""),
            "items": ocr_items,
            "entities": entities,
            "has_text": has_real_text,
            "word_count": len(full_text.split()) if has_real_text else 0
        }

    def _opencv_text_region_fallback(self, img_np: np.ndarray, w: int, h: int) -> List[Dict[str, Any]]:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)

        items = []
        bboxes = []
        for p in regions:
            x, y, box_w, box_h = cv2.boundingRect(p)
            if box_w < 12 or box_h < 8 or box_w > w * 0.9:
                continue
            bboxes.append((x, y, box_w, box_h))

        for box in bboxes:
            x, y, bw, bh = box
            x1 = round(x / w, 2)
            y1 = round(y / h, 2)
            x2 = round((x + bw) / w, 2)
            y2 = round((y + bh) / h, 2)
            
            items.append({
                "text": f"Text region at ({int(x1*100)}%, {int(y1*100)}%)",
                "confidence": 0.70,
                "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })
            if len(items) >= 4:
                break
        return items

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {"dates": [], "times": [], "urls": [], "numbers": [], "venues": []}

        dates = re.findall(r'\b(?:\d{1,2}[-/.\s]\d{1,2}[-/.\s]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b', text, re.IGNORECASE)
        times = re.findall(r'\b(?:\d{1,2}:\d{2}(?:\s?[AP]M)?|\d{1,2}\s?[AP]M)\b', text, re.IGNORECASE)
        urls = re.findall(r'https?://[^\s]+|www\.[^\s]+', text, re.IGNORECASE)
        numbers = re.findall(r'\b\d{5,}\b|\$\d+(?:\.\d{2})?', text)
        venues = re.findall(r'\b(?:Hall|Auditorium|Room|Campus|Building|Center|Block|Street|Lab)\s+[A-Z0-9-]+\b', text, re.IGNORECASE)

        return {
            "dates": list(set(dates)),
            "times": list(set(times)),
            "urls": list(set(urls)),
            "numbers": list(set(numbers)),
            "venues": list(set(venues))
        }

ocr_engine = OCREngine()
