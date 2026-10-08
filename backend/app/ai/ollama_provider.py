import httpx
import json
import base64
import asyncio
from typing import Dict, Any, List, Optional
from app.ai.provider import AIProvider
from app.ai.schemas import StructuredAIResponse
from app.ai.prompts import SYSTEM_PROMPT
from app.config import settings
from app.logging import logger

class OllamaProvider(AIProvider):
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL or "llava"

    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        from app.vision.verification_engine import verification_engine
        return await verification_engine.run_verification_pipeline(image_bytes, "Analyze scene")

    async def answer_question(
        self,
        image_bytes: bytes,
        question: str,
        evidence: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None
    ) -> StructuredAIResponse:
        
        target_model = model_name or self.model
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": target_model,
            "prompt": f"{SYSTEM_PROMPT}\nUser Question: {question}\nSupply structured JSON output.",
            "images": [img_b64],
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    raw_resp = res.json().get("response", "")
                    parsed = json.loads(raw_resp)
                    return StructuredAIResponse(**parsed)
        except Exception as e:
            logger.warning("ollama_provider_fallback", error=str(e))

        # Fallback to OpenAIProvider / Visual Verification Engine
        from app.ai.openai_provider import OpenAIProvider
        return await OpenAIProvider().answer_question(image_bytes, question, evidence, context, model_name)

    async def verify_claim(self, claim: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        from app.ai.openai_provider import OpenAIProvider
        return await OpenAIProvider().verify_claim(claim, evidence)

    async def summarize_image(self, evidence: Dict[str, Any]) -> str:
        from app.ai.openai_provider import OpenAIProvider
        return await OpenAIProvider().summarize_image(evidence)

    async def compare_images(self, image_a_bytes: bytes, image_b_bytes: bytes) -> Dict[str, Any]:
        from app.vision.comparator import image_comparator
        return image_comparator.compare_images(image_a_bytes, image_b_bytes)

    async def extract_structured_evidence(self, image_bytes: bytes) -> Dict[str, Any]:
        from app.vision.verification_engine import verification_engine
        return await verification_engine.run_verification_pipeline(image_bytes, "Extract structured evidence")
