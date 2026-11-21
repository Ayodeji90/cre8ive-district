export type MessageRole = "user" | "assistant" | "system";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
}

export interface Conversation {
  id: string;
  businessId?: string;
  status: "active" | "complete" | "archived";
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}
