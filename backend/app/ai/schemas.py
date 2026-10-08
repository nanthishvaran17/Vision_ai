from pydantic import BaseModel, Field
from typing import List, Optional

class StructuredAIResponse(BaseModel):
    observations: List[str] = Field(default_factory=list)
    inferences: List[str] = Field(default_factory=list)
    answer: str
    confidence: str = Field(default="MEDIUM", description="HIGH|MEDIUM|LOW|INSUFFICIENT")
    needs_verification: bool = False
    verification_reason: Optional[str] = ""
    suggested_followups: List[str] = Field(default_factory=list)
