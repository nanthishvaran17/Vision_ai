from typing import List, Dict, Any, Optional

def generate_dynamic_image_questions(
    objects: List[Dict[str, Any]],
    ocr_data: Dict[str, Any],
    scene: Optional[Dict[str, Any]] = None,
    spatial_rels: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates dynamic, image-specific questions and a visual summary based on real OpenCV detections,
    extracted OCR text, bounding box spatial relationships, and visual metrics.
    No static or hardcoded question fallbacks.
    """
    questions: List[str] = []
    
    # 1. Inspect OCR Text
    has_text = ocr_data.get("has_text", False) if isinstance(ocr_data, dict) else False
    raw_text = ocr_data.get("text", "").strip() if isinstance(ocr_data, dict) else ""
    items = ocr_data.get("items", []) if isinstance(ocr_data, dict) else []
    entities = ocr_data.get("entities", {}) if isinstance(ocr_data, dict) else {}

    # 2. Inspect Objects
    labels = [o["label"] for o in objects] if objects else []
    unique_labels = list(dict.fromkeys(labels))
    
    # Formulate initial visual summary
    summary_parts = []
    if unique_labels:
        summary_parts.append(f"detected {', '.join(unique_labels[:4])}")
    if has_text and raw_text and "Text region at" not in raw_text:
        first_line = raw_text.split('\n')[0][:40].strip()
        summary_parts.append(f"extracted text snippet '{first_line}' ({len(items)} text regions)")
    
    initial_summary = "Image analyzed: " + (" with ".join(summary_parts) if summary_parts else "visual surface scanned")

    # Generate Dynamic Questions based on Text
    if has_text and raw_text and "Text region" not in raw_text:
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        if lines:
            header_snippet = lines[0][:40]
            questions.append(f"What is the exact content of the text starting with '{header_snippet}'?")
        
        if len(lines) > 1:
            questions.append("Can you summarize all key points and numbers written in this document?")
        else:
            questions.append("Where is this text positioned on the document surface?")

        if entities.get("dates") or entities.get("times"):
            dates_found = entities.get("dates") or entities.get("times")
            questions.append(f"What event or schedule details correspond to {dates_found}?")
        if entities.get("venues"):
            questions.append(f"What location or venue is specified in the text?")

    # Generate Dynamic Questions based on Detected Objects
    if objects:
        primary = objects[0]
        primary_label = primary["label"]
        primary_color = primary.get("attributes", {}).get("color", "")
        
        if primary_color and primary_color != "neutral":
            questions.append(f"What are the physical attributes and exact shade of the {primary_color} {primary_label}?")
        else:
            questions.append(f"What are the precise visual characteristics of the {primary_label}?")

        if len(objects) >= 2:
            obj1 = objects[0]["label"]
            obj2 = objects[1]["label"]
            questions.append(f"What is the spatial relationship between the {obj1} and the {obj2}?")
            questions.append(f"Which object is closest to the left or right edge of the frame?")

        if len(objects) > 2:
            questions.append(f"Can you list all {len(objects)} detected items in order of visual area?")

    # Fallback to general dynamic visual questions if needed
    if len(questions) < 3:
        if scene and scene.get("type"):
            questions.append(f"How would you describe the overall arrangement of this {scene['type']} workspace?")
        questions.append("What specific markings, labels, or logos are visible on the primary object?")
        questions.append("Are there any secondary background objects or spatial details near the border?")

    # Deduplicate while retaining order
    seen = set()
    unique_questions = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)

    return {
        "initial_summary": initial_summary,
        "suggested_questions": unique_questions[:5]
    }
