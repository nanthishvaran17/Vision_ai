import math
from typing import Dict, Any, List
from app.vision.object_detector import object_detector
from app.vision.ocr import ocr_engine
from app.vision.scene_analyzer import scene_analyzer

class ImageComparator:
    def compare_images(self, image_a_bytes: bytes, image_b_bytes: bytes) -> Dict[str, Any]:
        """
        Compares Image A (Before) and Image B (After) from real pixel processing:
        Detects added objects, removed objects, moved objects, changed text/OCR, and scene lighting/color changes.
        """
        objects_a = object_detector.detect_objects(image_a_bytes)
        objects_b = object_detector.detect_objects(image_b_bytes)

        ocr_a = ocr_engine.extract_text(image_a_bytes)
        ocr_b = ocr_engine.extract_text(image_b_bytes)

        scene_a = scene_analyzer.analyze_scene(image_a_bytes)
        scene_b = scene_analyzer.analyze_scene(image_b_bytes)

        added_objects = []
        removed_objects = []
        moved_objects = []

        # Compare Object Detections
        labels_a = [o["label"] for o in objects_a]
        labels_b = [o["label"] for o in objects_b]

        for obj_b in objects_b:
            if obj_b["label"] not in labels_a:
                added_objects.append(obj_b)
            else:
                # Check for position movement
                match_a = next((o for o in objects_a if o["label"] == obj_b["label"]), None)
                if match_a:
                    box_a = match_a["box"]
                    box_b = obj_b["box"]
                    dist = math.sqrt(
                        ((box_a["x1"] + box_a["x2"])/2.0 - (box_b["x1"] + box_b["x2"])/2.0)**2 +
                        ((box_a["y1"] + box_a["y2"])/2.0 - (box_b["y1"] + box_b["y2"])/2.0)**2
                    )
                    if dist > 0.15:
                        moved_objects.append({
                            "label": obj_b["label"],
                            "from_box": box_a,
                            "to_box": box_b,
                            "shift_distance": round(dist, 3)
                        })

        for obj_a in objects_a:
            if obj_a["label"] not in labels_b:
                removed_objects.append(obj_a)

        # Compare Text
        text_a = ocr_a.get("text", "")
        text_b = ocr_b.get("text", "")
        changed_text = []
        if text_a != text_b:
            changed_text.append({
                "before_text": text_a,
                "after_text": text_b
            })

        # Summary Generation
        changes_summary_parts = []
        if added_objects:
            changes_summary_parts.append(f"Added {len(added_objects)} object(s): " + ", ".join(o["label"] for o in added_objects))
        if removed_objects:
            changes_summary_parts.append(f"Removed {len(removed_objects)} object(s): " + ", ".join(o["label"] for o in removed_objects))
        if moved_objects:
            changes_summary_parts.append(f"Moved {len(moved_objects)} object(s): " + ", ".join(m["label"] for m in moved_objects))
        if changed_text:
            changes_summary_parts.append("Text content changed between images.")

        if not changes_summary_parts:
            summary = "No significant structural differences detected between Image A and Image B."
        else:
            summary = " | ".join(changes_summary_parts)

        return {
            "added_objects": added_objects,
            "removed_objects": removed_objects,
            "moved_objects": moved_objects,
            "changed_text": changed_text,
            "scene_before": scene_a,
            "scene_after": scene_b,
            "summary": summary
        }

image_comparator = ImageComparator()
