from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column, String, Text, Float, Boolean, Integer, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="USER", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Verification Chat")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    images = relationship("ImageRecord", back_populates="conversation", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="USER_TEXT", nullable=False)  # USER_TEXT, USER_IMAGE, AI_RESPONSE, EVIDENCE, VERIFICATION, ERROR, SYSTEM
    metadata_json = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    conversation = relationship("Conversation", back_populates="messages")
    images = relationship("ImageRecord", back_populates="message", cascade="all, delete-orphan")
    verification_runs = relationship("VerificationRun", back_populates="message", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="message", cascade="all, delete-orphan")

__table_args__ = (
    Index("idx_messages_conversation_created", "conversation_id", "created_at"),
)

class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    file_path = Column(String(512), nullable=False)
    thumbnail_path = Column(String(512), nullable=True)
    sha256 = Column(String(64), nullable=False, index=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    conversation = relationship("Conversation", back_populates="images")
    message = relationship("Message", back_populates="images")
    visual_objects = relationship("VisualObject", back_populates="image", cascade="all, delete-orphan")
    visual_evidence = relationship("VisualEvidence", back_populates="image", cascade="all, delete-orphan")
    verification_runs = relationship("VerificationRun", back_populates="image", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="image", cascade="all, delete-orphan")

class VisualObject(Base):
    __tablename__ = "visual_objects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    x1 = Column(Float, nullable=False)  # Normalized 0-1
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    attributes_json = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), default=utc_now)

    image = relationship("ImageRecord", back_populates="visual_objects")

class VisualEvidence(Base):
    __tablename__ = "visual_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(100), nullable=False)  # object_detection, ocr, spatial, scene
    source = Column(String(100), nullable=False)
    content_json = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    image = relationship("ImageRecord", back_populates="visual_evidence")

class VerificationRun(Base):
    __tablename__ = "verification_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    question = Column(Text, nullable=False)
    initial_answer = Column(Text, nullable=False)
    initial_confidence = Column(String(50), nullable=False)  # HIGH, MEDIUM, LOW, INSUFFICIENT
    verification_required = Column(Boolean, default=False)
    verification_steps_json = Column(Text, nullable=True)  # JSON list of steps
    final_confidence = Column(String(50), nullable=False)
    status = Column(String(50), default="COMPLETED")  # COMPLETED, FAILED, IN_PROGRESS
    created_at = Column(DateTime(timezone=True), default=utc_now)

    image = relationship("ImageRecord", back_populates="verification_runs")
    message = relationship("Message", back_populates="verification_runs")
    claims = relationship("Claim", back_populates="verification_run", cascade="all, delete-orphan")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    verification_run_id = Column(String(36), ForeignKey("verification_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    supported = Column(Boolean, nullable=False)
    evidence_ids_json = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    verification_run = relationship("VerificationRun", back_populates="claims")

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # box, polygon, text
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    label = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    image = relationship("ImageRecord", back_populates="annotations")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    bounding_boxes_json = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    language = Column(String(50), default="en")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    image = relationship("ImageRecord", back_populates="ocr_results")

class ImageComparison(Base):
    __tablename__ = "image_comparisons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_a_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    image_b_id = Column(String(36), ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    differences_json = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime(timezone=True), default=utc_now)

class ConversationContext(Base):
    __tablename__ = "conversation_context"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    referenced_object_ids_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    conversation = relationship("Conversation", back_populates="contexts")
    message = relationship("Message", back_populates="contexts")
