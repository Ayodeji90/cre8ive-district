import type { Conversation } from "@cre8ive/types";
import { apiClient } from "./client";

export interface StartChatResponse {
  conversation_id: string;
  greeting: string;
}

export const chatApi = {
  start: (idea: string) => apiClient.request<StartChatResponse>("/api/chat/start", {
    method: "POST",
    body: JSON.stringify({ idea }),
  }),
  history: (id: string) => apiClient.request<Conversation>(`/api/chat/${encodeURIComponent(id)}/history`),
};
