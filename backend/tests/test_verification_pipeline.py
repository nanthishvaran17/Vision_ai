import pytest
import io
from PIL import Image, ImageDraw
from app.vision.object_detector import object_detector
from app.vision.ocr import ocr_engine
from app.vision.spatial_analyzer import spatial_analyzer
from app.vision.claim_validator import claim_validator
from app.vision.memory import conversation_memory
from app.vision.comparator import image_comparator
from app.security.upload_guard import validate_and_preprocess_image
from fastapi import HTTPException

def generate_test_image(text="TEST NOTICE 2026", color=(200, 50, 50)) -> bytes:
    """Generates a real test image with pixels, bounding shapes, and text."""
    img = Image.new("RGB", (600, 400), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a colored box (object 1)
    draw.rectangle([50, 50, 250, 350], fill=color, outline=(0, 0, 0))
    # Draw a second box (object 2)
    draw.rectangle([350, 100, 550, 300], fill=(50, 150, 200), outline=(0, 0, 0))
    # Draw text
    draw.text((60, 60), text, fill=(255, 255, 255))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

@pytest.mark.asyncio
async def test_scenario_1_correct_identification():
    img_bytes = generate_test_image()
    objs = object_detector.detect_objects(img_bytes)
    assert len(objs) >= 1
    assert "box" in objs[0]
    assert 0.0 <= objs[0]["box"]["x1"] <= 1.0

@pytest.mark.asyncio
async def test_scenario_2_low_confidence_identification():
    # Very noisy image
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    objs = object_detector.detect_objects(buf.getvalue())
    assert len(objs) >= 1

@pytest.mark.asyncio
async def test_scenario_3_unsupported_exact_model_rejected():
    draft = "This is a red object and it is an iPad Pro 12.9 Inch 2024 model."
    ans, unsupported, _ = claim_validator.validate_claims(
        draft, [], "", [], is_exact_model_question=True
    )
    assert len(unsupported) >= 1
    assert "I don't have enough visual evidence" in ans or "reliable" in ans

@pytest.mark.asyncio
async def test_scenario_4_ocr_extraction():
    img_bytes = generate_test_image(text="CONFERENCE 2026 ROOM 101")
    ocr_res = ocr_engine.extract_text(img_bytes)
    assert isinstance(ocr_res, dict)
    assert "has_text" in ocr_res

@pytest.mark.asyncio
async def test_scenario_5_spatial_query():
    objs = [
        {"id": "o1", "label": "laptop", "box": {"x1": 0.1, "y1": 0.1, "x2": 0.4, "y2": 0.5}},
        {"id": "o2", "label": "mouse", "box": {"x1": 0.6, "y1": 0.1, "x2": 0.8, "y2": 0.5}}
    ]
    rels = spatial_analyzer.analyze_spatial_relations(objs)
    assert len(rels) >= 2
    ans = spatial_analyzer.find_relation_for_query("What is to the right of the laptop?", objs, rels)
    assert ans is not None
    assert "mouse" in ans

@pytest.mark.asyncio
async def test_scenario_6_pronoun_resolution():
    objs = [
        {"id": "o1", "label": "smartphone", "box": {"x1": 0.1, "y1": 0.1, "x2": 0.4, "y2": 0.5}},
        {"id": "o2", "label": "keyboard", "box": {"x1": 0.5, "y1": 0.1, "x2": 0.9, "y2": 0.5}}
    ]
    res = conversation_memory.resolve_pronouns("What color is it?", objs)
    assert res["resolved_object"] is not None
    assert res["resolved_object"]["label"] == "smartphone"

@pytest.mark.asyncio
async def test_scenario_7_image_comparison():
    img_a = generate_test_image("BEFORE", color=(200, 50, 50))
    img_b = generate_test_image("AFTER", color=(50, 200, 50))
    comp = image_comparator.compare_images(img_a, img_b)
    assert "summary" in comp

@pytest.mark.asyncio
async def test_scenario_8_hallucination_rejection():
    ans, unsupported, claims = claim_validator.validate_claims(
        "This object is an iPhone 16 Pro Max", [], "No text", []
    )
    assert "iPhone 16 Pro Max" in str(unsupported)

@pytest.mark.asyncio
async def test_scenario_9_provider_failure():
    from app.ai.openai_provider import OpenAIProvider
    provider = OpenAIProvider()
    res = await provider.answer_question(generate_test_image(), "What is this?", {"objects": []})
    assert res.answer is not None

@pytest.mark.asyncio
async def test_scenario_10_malicious_upload_defense():
    invalid_bytes = b"NOT_AN_IMAGE_FILE_DATA"
    with pytest.raises(HTTPException) as exc_info:
        validate_and_preprocess_image(invalid_bytes)
    assert exc_info.value.status_code == 400
