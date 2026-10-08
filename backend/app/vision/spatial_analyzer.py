import math
from typing import List, Dict, Any, Optional

class SpatialAnalyzer:
    def analyze_spatial_relations(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates exact deterministic spatial geometric relationships between detected objects
        using normalized bounding boxes [x1, y1, x2, y2].
        """
        if not objects or len(objects) < 2:
            return []

        relations = []

        for i in range(len(objects)):
            for j in range(len(objects)):
                if i == j:
                    continue

                obj_a = objects[i]
                obj_b = objects[j]

                box_a = obj_a["box"]
                box_b = obj_b["box"]

                # Centroids
                cx_a = (box_a["x1"] + box_a["x2"]) / 2.0
                cy_a = (box_a["y1"] + box_a["y2"]) / 2.0

                cx_b = (box_b["x1"] + box_b["x2"]) / 2.0
                cy_b = (box_b["y1"] + box_b["y2"]) / 2.0

                # Euclidean distance between centroids
                dist = math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)

                # Directional checks
                dx = cx_b - cx_a
                dy = cy_b - cy_a

                # Overlap calculation (Intersection over Area A)
                ix1 = max(box_a["x1"], box_b["x1"])
                iy1 = max(box_a["y1"], box_b["y1"])
                ix2 = min(box_a["x2"], box_b["x2"])
                iy2 = min(box_a["y2"], box_b["y2"])

                inter_w = max(0.0, ix2 - ix1)
                inter_h = max(0.0, iy2 - iy1)
                inter_area = inter_w * inter_h

                area_a = (box_a["x2"] - box_a["x1"]) * (box_a["y2"] - box_a["y1"])
                area_b = (box_b["x2"] - box_b["x1"]) * (box_b["y2"] - box_b["y1"])

                is_inside = (
                    box_a["x1"] >= box_b["x1"] and box_a["x2"] <= box_b["x2"] and
                    box_a["y1"] >= box_b["y1"] and box_a["y2"] <= box_b["y2"]
                )

                is_overlapping = inter_area > 0.05 * min(area_a, area_b)

                if is_inside:
                    rel_type = "inside"
                elif is_overlapping:
                    rel_type = "overlapping"
                elif abs(dx) > abs(dy):
                    rel_type = "right_of" if dx > 0 else "left_of"
                else:
                    rel_type = "below" if dy > 0 else "above"

                proximity = "near" if dist < 0.35 else "far"

                relations.append({
                    "subject_id": obj_a["id"],
                    "subject_label": obj_a["label"],
                    "relation": rel_type,
                    "proximity": proximity,
                    "object_id": obj_b["id"],
                    "object_label": obj_b["label"],
                    "distance": round(dist, 3)
                })

        # Find closest and farthest for each object
        for obj in objects:
            obj_rels = [r for r in relations if r["subject_id"] == obj["id"]]
            if obj_rels:
                closest = min(obj_rels, key=lambda r: r["distance"])
                farthest = max(obj_rels, key=lambda r: r["distance"])

                relations.append({
                    "subject_id": obj["id"],
                    "subject_label": obj["label"],
                    "relation": "closest_to",
                    "object_id": closest["object_id"],
                    "object_label": closest["object_label"],
                    "distance": closest["distance"]
                })
                relations.append({
                    "subject_id": obj["id"],
                    "subject_label": obj["label"],
                    "relation": "farthest_from",
                    "object_id": farthest["object_id"],
                    "object_label": farthest["object_label"],
                    "distance": farthest["distance"]
                })

        return relations

    def find_relation_for_query(self, query: str, objects: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Optional[str]:
        """
        Resolves a spatial question (e.g. "What's next to the laptop?", "What is to the left of the bottle?")
        using deterministic spatial geometry.
        """
        query_lower = query.lower()
        
        # Determine target relation requested
        target_rel = None
        if "next to" in query_lower or "near" in query_lower or "beside" in query_lower:
            target_rel = "near"
        elif "left" in query_lower:
            target_rel = "left_of"
        elif "right" in query_lower:
            target_rel = "right_of"
        elif "above" in query_lower or "top" in query_lower:
            target_rel = "above"
        elif "below" in query_lower or "under" in query_lower or "bottom" in query_lower:
            target_rel = "below"
        elif "inside" in query_lower or "in" in query_lower:
            target_rel = "inside"

        # Match object mentioned in query
        matched_obj = None
        for obj in objects:
            label_words = obj["label"].lower().split()
            for word in label_words:
                if len(word) > 3 and word in query_lower:
                    matched_obj = obj
                    break
            if matched_obj:
                break

        if matched_obj and target_rel:
            matching_rels = [
                r for r in relations 
                if (r["object_id"] == matched_obj["id"] or r["subject_id"] == matched_obj["id"])
            ]
            if matching_rels:
                res = matching_rels[0]
                return f"Based on spatial geometry, {res['subject_label']} is {res['relation']} {res['object_label']} (distance: {res['distance']})."

        return None

spatial_analyzer = SpatialAnalyzer()
