from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# --- Object Detection & Evidence Schemas ---
class BoundingBox(BaseModel):
    x1: float = Field(..., ge=0.0, le=1.0)
    y1: float = Field(..., ge=0.0, le=1.0)
    x2: float = Field(..., ge=0.0, le=1.0)
    y2: float = Field(..., ge=0.0, le=1.0)

class DetectedObject(BaseModel):
    id: str
    label: str
    confidence: float
    box: BoundingBox
    attributes: Dict[str, Any] = {}

class OCRItem(BaseModel):
    text: str
    box: BoundingBox
    confidence: float

class SpatialRelation(BaseModel):
    subject: str
    relation: str  # left_of, right_of, above, below, inside, outside, near, far, overlapping, closest_to, farthest_from
    object: str
    distance: float

class EvidenceItem(BaseModel):
    type: str  # object_detection, ocr, spatial_relation, scene_analysis, crop_analysis
    source: str
    description: str
    confidence: float
    details: Optional[Dict[str, Any]] = None

class EvidenceScores(BaseModel):
    visual_detection_score: float
    ocr_score: float
    spatial_score: float
    context_score: float
    cross_check_score: float
    evidence_score: float
    level: str  # HIGH, MEDIUM, LOW, INSUFFICIENT

# --- Verification & Grounding Schemas ---
class VerificationStepLog(BaseModel):
    step: str
    status: str  # STARTED, COMPLETED, SKIPPED, FAILED
    description: str
    timestamp: datetime
    evidence_found: Optional[Dict[str, Any]] = None

class ClaimValidationResult(BaseModel):
    claim_text: str
    supported: bool
    confidence: float
    evidence_ids: List[str] = []

class WhyThisAnswerPayload(BaseModel):
    question: str
    answer: str
    confidence: str  # HIGH, MEDIUM, LOW, INSUFFICIENT
    evidence_level: str
    evidence: List[EvidenceItem]
    verification_steps: List[str]
    unsupported_claims: List[str]
    annotations: List[DetectedObject]

# --- Message & Conversation Schemas ---
class MessageCreate(BaseModel):
    conversation_id: str
    content: str
    image_id: Optional[str] = None
    message_type: str = "USER_TEXT"
    is_challenge: bool = False

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    message_type: str
    metadata_json: Optional[str] = None
    created_at: datetime
    why_this_answer: Optional[WhyThisAnswerPayload] = None

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Verification Chat"

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None

# --- Image Upload & Analysis Schemas ---
class ImageUploadResponse(BaseModel):
    id: str
    conversation_id: str
    file_path: str
    thumbnail_path: str
    sha256: str
    width: int
    height: int
    mime_type: str
    objects_count: int
    ocr_text_length: int

class ImageComparisonRequest(BaseModel):
    image_a_id: str
    image_b_id: str

class ImageComparisonResponse(BaseModel):
    id: str
    image_a_id: str
    image_b_id: str
    added_objects: List[DetectedObject]
    removed_objects: List[DetectedObject]
    moved_objects: List[Dict[str, Any]]
    changed_text: List[Dict[str, Any]]
    summary: str

# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str
    database: str
    ai_provider: str
    ocr_engine: str
    version: str
    uptime_seconds: float
