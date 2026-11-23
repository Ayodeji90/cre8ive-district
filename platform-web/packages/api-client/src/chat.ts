import { apiClient } from './client'

// ---------------------------------------------------------------------------
// Legacy start (kept for compatibility; new flows use resume + state instead)
// ---------------------------------------------------------------------------

export interface StartChatRequest {
  user_id?: string
  business_id?: string
  initial_idea?: string
}

export interface StartChatResponse {
  conversation_id: string
  greeting_message: string
  context: Record<string, unknown>
}

// ---------------------------------------------------------------------------
// Chat messages / history (legacy, kept for compat)
// ---------------------------------------------------------------------------

export interface ChatMessage {
  id: string
  conversation_id: string
  direction: 'inbound' | 'outbound'
  content: string
  media_url?: string | null
  media_type?: string | null
  role: 'customer' | 'assistant' | 'system'
  created_at: string
}

export interface ChatHistoryResponse {
  conversation_id: string
  messages: ChatMessage[]
  context: Record<string, unknown>
  total: number
  page: number
  limit: number
}

// ---------------------------------------------------------------------------
// Resume — mirrors POST /api/businesses/{business_id}/chat/resume
// ---------------------------------------------------------------------------

export interface ChatResumeRequest {
  initial_idea?: string | null
}

export interface ChatResumeResponse {
  conversation_id: string
  mode: 'resumed' | 'new'
  business_id: string
  context: Record<string, unknown>
  greeting: string | null
}

export const chatApi = {
  /** Legacy endpoint (deprecated for new flows). */
  start: (payload?: string | StartChatRequest) => {
    const body = typeof payload === 'string' ? { initial_idea: payload } : (payload ?? {})
    return apiClient.request<StartChatResponse>('/api/chat/start', {
      method: 'POST',
      body: JSON.stringify(body),
    })
  },
  history: (id: string, page = 1, limit = 50) =>
    apiClient.request<ChatHistoryResponse>(
      `/api/chat/${encodeURIComponent(id)}/history?page=${page}&limit=${limit}`
    ),
  /** POST /api/businesses/{business_id}/chat/resume */
  resume: (businessId: string, body: ChatResumeRequest) =>
    apiClient.request<ChatResumeResponse>(
      `/api/businesses/${encodeURIComponent(businessId)}/chat/resume`,
      {
        method: 'POST',
        body: JSON.stringify(body),
      }
    ),
}
