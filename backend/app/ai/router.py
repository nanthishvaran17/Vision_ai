from typing import Dict, Any
from app.config import settings

class ModelRouter:
    def route_request(self, question: str, initial_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Model router rule:
        - Text question -> OCR engine priority
        - Relation question -> spatial analyzer geometry priority
        - Simple question -> cheaper VISION_MODEL
        - Complex verification / exact model -> STRONG_MODEL
        """
        q_lower = question.lower()

        is_exact = any(w in q_lower for w in ["exact model", "brand", "make", "serial", "part number"])
        is_text = any(w in q_lower for w in ["text", "read", "written", "notice", "date", "time"])
        is_spatial = any(w in q_lower for w in ["next to", "left of", "right of", "above", "below", "near"])

        if is_exact:
            selected_model = settings.STRONG_MODEL
            pipeline_type = "COMPLEX_VERIFICATION"
        elif is_text:
            selected_model = settings.VISION_MODEL
            pipeline_type = "OCR_PRIMARY"
        elif is_spatial:
            selected_model = settings.VISION_MODEL
            pipeline_type = "SPATIAL_PRIMARY"
        else:
            selected_model = settings.VISION_MODEL
            pipeline_type = "STANDARD_VISION"

        return {
            "selected_model": selected_model,
            "pipeline_type": pipeline_type,
            "routing_reason": f"Routed to {selected_model} via {pipeline_type} pipeline based on query intents."
        }

model_router = ModelRouter()
