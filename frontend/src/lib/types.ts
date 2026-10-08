export interface User {
  id: string;
  email: string;
  name: string;
  role: 'USER' | 'ADMIN';
  created_at: string;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectedObject {
  id: string;
  label: string;
  confidence: number;
  box: BoundingBox;
  attributes?: Record<string, any>;
}

export interface EvidenceItem {
  type: string;
  source: string;
  description: string;
  confidence: number;
  details?: Record<string, any>;
}

export interface WhyThisAnswerPayload {
  question: string;
  answer: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT';
  evidence_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT';
  evidence: EvidenceItem[];
  verification_steps: string[];
  unsupported_claims: string[];
  annotations: DetectedObject[];
  suggested_questions?: string[];
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type: 'USER_TEXT' | 'USER_IMAGE' | 'AI_RESPONSE' | 'EVIDENCE' | 'VERIFICATION' | 'ERROR' | 'SYSTEM';
  created_at: string;
  why_this_answer?: WhyThisAnswerPayload;
  metadata_json?: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message?: string;
}

export interface ImageRecordResponse {
  id: string;
  conversation_id: string;
  file_path: string;
  thumbnail_path?: string;
  sha256: string;
  width: number;
  height: number;
  mime_type: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  images?: ImageRecordResponse[];
}

export interface ImageUploadResponse {
  id: string;
  conversation_id: string;
  file_path: string;
  thumbnail_path: string;
  sha256: string;
  width: number;
  height: number;
  mime_type: string;
  objects_count: number;
  ocr_text_length: number;
  suggested_questions?: string[];
  initial_summary?: string;
}


export interface ImageComparisonResponse {
  id: string;
  image_a_id: string;
  image_b_id: string;
  added_objects: DetectedObject[];
  removed_objects: DetectedObject[];
  moved_objects: Array<{ label: string; shift_distance: number }>;
  changed_text: Array<{ before_text: string; after_text: string }>;
  summary: string;
}
