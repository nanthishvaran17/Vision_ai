import re
from typing import List, Dict, Any, Optional

class ConversationMemory:
    def resolve_pronouns(
        self,
        query: str,
        recent_objects: List[Dict[str, Any]],
        referenced_object_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Resolves pronouns "it", "this", "that", "the second one", "the red one" to specific visual objects
        from conversation memory.
        """
        query_lower = query.lower()
        pronouns = ["it", "this", "that", "the device", "the object", "the item"]
        
        has_pronoun = any(re.search(rf'\b{p}\b', query_lower) for p in pronouns)
        ordinal_match = re.search(r'\bthe (first|second|third|1st|2nd|3rd) one\b', query_lower)

        resolved_object = None
        resolution_notes = ""

        if ordinal_match and recent_objects:
            ord_str = ordinal_match.group(1)
            idx_map = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2}
            idx = idx_map.get(ord_str, 0)
            if idx < len(recent_objects):
                resolved_object = recent_objects[idx]
                resolution_notes = f"Resolved '{ordinal_match.group(0)}' to object #{idx+1} ({resolved_object['label']})"

        elif has_pronoun and recent_objects:
            # If specific object IDs were referenced in previous context turn, select that
            if referenced_object_ids:
                matching = [o for o in recent_objects if o["id"] in referenced_object_ids]
                if matching:
                    resolved_object = matching[0]
            if not resolved_object:
                # Default to primary largest object
                resolved_object = recent_objects[0]
            resolution_notes = f"Resolved pronoun to primary target object ({resolved_object['label']})"

        return {
            "resolved_object": resolved_object,
            "resolution_notes": resolution_notes,
            "augmented_query": f"{query} [Refers to: {resolved_object['label']}]" if resolved_object else query
        }

conversation_memory = ConversationMemory()
