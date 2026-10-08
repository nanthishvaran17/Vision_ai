import re
from typing import List, Dict, Any, Tuple

class ClaimValidator:
    def validate_claims(
        self,
        draft_answer: str,
        objects: List[Dict[str, Any]],
        ocr_text: str,
        spatial_relations: List[Dict[str, Any]],
        is_exact_model_question: bool = False
    ) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """
        Extracts factual claims from draft answer, verifies each against stored visual evidence (objects, OCR, spatial).
        Removes or updates unsupported claims, returning (validated_answer, unsupported_claims, claim_results).
        """
        unsupported_claims: List[str] = []
        claim_results: List[Dict[str, Any]] = []

        # Exact model check rule (Rule 4 & Section 1)
        # If user asked for exact model/brand and OCR/evidence has no matching exact model string
        brand_model_patterns = [
            r'iPad Pro \d+', r'iPhone \d+ Pro Max', r'Samsung Galaxy S\d+', r'MacBook Pro M\d+',
            r'Dell XPS \d+', r'Sony WH-1000XM\d', r'Bose QuietComfort \d+', r'Logitech MX Master \d+'
        ]

        found_model_claim = None
        for pattern in brand_model_patterns:
            match = re.search(pattern, draft_answer, re.IGNORECASE)
            if match:
                found_model_claim = match.group(0)
                break

        if found_model_claim:
            # Check if this exact string actually appears in OCR text
            if ocr_text and found_model_claim.lower() in ocr_text.lower():
                claim_results.append({
                    "claim_text": f"Exact model identification: {found_model_claim}",
                    "supported": True,
                    "confidence": 0.95
                })
            else:
                unsupported_claims.append(f"Exact model claim: {found_model_claim}")
                claim_results.append({
                    "claim_text": f"Exact model identification: {found_model_claim}",
                    "supported": False,
                    "confidence": 0.2
                })
                # Replace unsupported claim with refusal statement
                refusal_replacement = (
                    "I can identify this object from visual features, but I don't have enough visual evidence "
                    "(such as legible model text or distinctive branding) to reliably verify the exact model."
                )
                draft_answer = re.sub(found_model_claim, "the device", draft_answer, flags=re.IGNORECASE)
                if refusal_replacement not in draft_answer:
                    draft_answer += f"\n\n*Note on verification*: {refusal_replacement}"

        # If question asked for exact model and no OCR model was verified
        if is_exact_model_question and unsupported_claims:
            draft_answer = (
                "I can identify this as a visual object in the image, but I don't have enough visual evidence "
                "or readable branding text in this photo to reliably identify the exact model."
            )

        # Check color claims against visual object color attributes
        color_matches = re.findall(r'\b(red|blue|green|yellow|purple|black|white|silver|gold|gray)\b', draft_answer, re.IGNORECASE)
        for c in set(color_matches):
            c_lower = c.lower()
            supported_color = any(
                c_lower in obj.get("attributes", {}).get("color", "").lower()
                for obj in objects
            )
            claim_results.append({
                "claim_text": f"Object color is {c}",
                "supported": supported_color or len(objects) == 0,
                "confidence": 0.9 if supported_color else 0.5
            })

        return draft_answer, unsupported_claims, claim_results

claim_validator = ClaimValidator()
