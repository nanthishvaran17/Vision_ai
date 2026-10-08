# VisionNext AI — Judge Demo Script

## End-to-End Judge Demonstration Steps

1. **Upload Complex Object Photo**:
   - Upload photo of desk/room containing multiple items.
   - Observe real runtime object detection boxes with normalized bounds.
2. **Deterministic Spatial Reasoning**:
   - Ask: *"What is to the right of the laptop?"*
   - System calculates normalized centroid matrix and answers with exact spatial geometry.
3. **Pronoun Conversation Memory**:
   - Ask: *"What color is it?"*
   - Memory engine resolves *"it"* to the previously discussed visual object.
4. **Exact Model Refusal & Audit Trail**:
   - Ask: *"What exact model is this tablet?"*
   - System triggers Active Crop & Zoom, detects insufficient model text, and displays:
     *"I can identify this as a tablet, but I don't have enough visual evidence to reliably identify the exact model."*
   - Click **"Show me why"** to inspect the evidence level and audit trail.
5. **Notice Document OCR & Entity Extraction**:
   - Upload a college notice / event flyer.
   - Ask: *"When and where is the event?"*
   - OCR engine reads notice text and extracts dates, times, and venue locations.
6. **Compare Mode**:
   - Navigate to `/compare`.
   - Upload Image A (Before) and Image B (After).
   - View detected added objects, removed objects, and moved position diffs.
