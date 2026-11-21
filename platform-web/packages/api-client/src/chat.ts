import { apiClient } from "./client";

export interface StartChatRequest {
  user_id?: string;
  business_id?: string;
  initial_idea?: string;
}

export interface StartChatResponse {
  conversation_id: string;
  greeting_message: string;
  context: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  direction: "inbound" | "outbound";
  content: string;
  media_url?: string | null;
  media_type?: string | null;
  role: "customer" | "assistant" | "system";
  created_at: string;
}

export interface ChatHistoryResponse {
  conversation_id: string;
  messages: ChatMessage[];
  context: Record<string, unknown>;
  total: number;
  page: number;
  limit: number;
}

export const chatApi = {
  start: (payload?: string | StartChatRequest) => {
    const body = typeof payload === "string" ? { initial_idea: payload } : (payload ?? {});
    return apiClient.request<StartChatResponse>("/api/chat/start", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  history: (id: string, page = 1, limit = 50) =>
    apiClient.request<ChatHistoryResponse>(
      `/api/chat/${encodeURIComponent(id)}/history?page=${page}&limit=${limit}`
    ),
};
