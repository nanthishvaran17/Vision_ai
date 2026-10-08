from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.ai.schemas import StructuredAIResponse

class AIProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def answer_question(
        self,
        image_bytes: bytes,
        question: str,
        evidence: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None
    ) -> StructuredAIResponse:
        pass

    @abstractmethod
    async def verify_claim(self, claim: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def summarize_image(self, evidence: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def compare_images(self, image_a_bytes: bytes, image_b_bytes: bytes) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def extract_structured_evidence(self, image_bytes: bytes) -> Dict[str, Any]:
        pass
