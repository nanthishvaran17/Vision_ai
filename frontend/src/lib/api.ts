import { User, ConversationSummary, Conversation, Message, ImageUploadResponse, ImageComparisonResponse, DetectedObject } from './types';

const API_BASE = '/api/v1';

export function getAuthToken(): string | null {
  return localStorage.getItem('access_token');
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  
  if (res.status === 401) {
    clearTokens();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  return res;
}

export const api = {
  // Auth
  register: async (email: string, name: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  login: async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  getMe: async (): Promise<User> => {
    const res = await fetchWithAuth('/auth/me');
    return res.json();
  },

  // Conversations
  listConversations: async (): Promise<ConversationSummary[]> => {
    const res = await fetchWithAuth('/conversations');
    return res.json();
  },

  createConversation: async (title?: string): Promise<Conversation> => {
    const res = await fetchWithAuth('/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || 'New Verification Chat' })
    });
    return res.json();
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const res = await fetchWithAuth(`/conversations/${id}`);
    return res.json();
  },

  deleteConversation: async (id: string) => {
    const res = await fetchWithAuth(`/conversations/${id}`, { method: 'DELETE' });
    return res.json();
  },

  // Messages
  sendMessage: async (conversation_id: string, content: string, image_id?: string, is_challenge: boolean = false): Promise<Message> => {
    const res = await fetchWithAuth('/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id, content, image_id, is_challenge })
    });
    return res.json();
  },

  // Image Upload
  uploadImage: async (conversation_id: string, file: File): Promise<ImageUploadResponse> => {
    const formData = new FormData();
    formData.append('conversation_id', conversation_id);
    formData.append('file', file);

    const token = getAuthToken();
    const res = await fetch(`${API_BASE}/images/upload`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Image upload failed');
    }
    return res.json();
  },

  // Image Objects
  getImageObjects: async (imageId: string): Promise<DetectedObject[]> => {
    const res = await fetchWithAuth(`/images/${imageId}/objects`);
    return res.json();
  },

  // Image Comparison
  compareImages: async (image_a_id: string, image_b_id: string): Promise<ImageComparisonResponse> => {
    const res = await fetchWithAuth('/vision/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_a_id, image_b_id })
    });
    return res.json();
  }
};
