"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { chatApi, type StartChatResponse, type ChatMessage } from "@cre8ive/api-client";

export interface ChatMessageItem {
  id: string;
  role: "customer" | "assistant" | "system";
  content: string;
  createdAt: string;
  isStreaming?: boolean;
}

export interface ExtractedBrandContext {
  conversation_stage?: string;
  business_name?: string;
  description?: string;
  industry?: string;
  target_audience?: string;
  style_keywords?: string[];
  mood?: string;
  ready_to_generate?: boolean;
  [key: string]: unknown;
}

function resolveWsUrl(conversationId: string, token?: string | null): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const wsBase = apiUrl.replace(/^http:\/\//, "ws://").replace(/^https:\/\//, "wss://");
  const query = token ? `?token=${encodeURIComponent(token)}` : "";
  return `${wsBase}/api/chat/${encodeURIComponent(conversationId)}${query}`;
}

export function useAbijaChat(initialConversationId?: string, accessToken?: string | null) {
  const [conversationId, setConversationId] = useState<string | null>(initialConversationId ?? null);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const [context, setContext] = useState<ExtractedBrandContext>({
    conversation_stage: "greeting",
    ready_to_generate: false,
  });
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isThinking, setIsThinking] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamingAccRef = useRef<string>("");

  // Connect WebSocket when conversationId is available
  useEffect(() => {
    if (!conversationId) return;

    let isUnmounted = false;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let reconnectAttempts = 0;

    function connect() {
      if (isUnmounted) return;
      const wsUrl = resolveWsUrl(conversationId!, accessToken);
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        if (isUnmounted) return;
        setIsConnected(true);
        setError(null);
        reconnectAttempts = 0;
        // Heartbeat every 25 seconds
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, 25000);
      };

      ws.onmessage = (event) => {
        if (isUnmounted) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === "ready") {
            if (data.context) {
              setContext((prev) => ({ ...prev, ...data.context }));
            }
          } else if (data.type === "chunk") {
            setIsThinking(false);
            streamingAccRef.current += data.content ?? "";
            setStreamingContent(streamingAccRef.current);
          } else if (data.type === "done") {
            const finalContent = data.content || streamingAccRef.current;
            setMessages((prev) => [
              ...prev,
              {
                id: `msg-${Date.now()}`,
                role: "assistant",
                content: finalContent,
                createdAt: new Date().toISOString(),
              },
            ]);
            streamingAccRef.current = "";
            setStreamingContent("");
            setIsThinking(false);
            if (data.context) {
              setContext((prev) => ({ ...prev, ...data.context }));
            }
          } else if (data.type === "generation_started") {
            if (data.business_id) {
              setContext((prev) => ({
                ...prev,
                business_id: data.business_id,
                ready_to_generate: true,
              }));
            }
          } else if (data.type === "error") {
            setError(data.detail ?? "Something went wrong. Please try again.");
            setIsThinking(false);
            streamingAccRef.current = "";
            setStreamingContent("");
          }
        } catch (err) {
          console.error("Failed to parse websocket message", err);
        }
      };

      ws.onerror = () => {
        if (!isUnmounted) {
          setIsConnected(false);
        }
      };

      ws.onclose = (event) => {
        if (isUnmounted) return;
        setIsConnected(false);
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Do not reconnect on auth errors
        if (event.code === 4401 || event.code === 4403) {
          setError("Authentication required or access denied. Please refresh or sign in.");
          return;
        }

        if (reconnectAttempts < 5) {
          reconnectAttempts += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 16000);
          setError(`Disconnected. Reconnecting in ${Math.round(delay / 1000)}s...`);
          reconnectTimeout = setTimeout(() => {
            if (!isUnmounted) {
              connect();
            }
          }, delay);
        } else {
          setError("Connection lost. Please refresh the page to reconnect.");
        }
      };
    }

    connect();

    return () => {
      isUnmounted = true;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [conversationId, accessToken]);

  // Start new conversation
  const startConversation = useCallback(
    async (initialIdea?: string, businessId?: string): Promise<StartChatResponse | null> => {
      try {
        setError(null);
        setIsThinking(true);
        const payload: { initial_idea?: string; business_id?: string } = {};
        if (initialIdea && initialIdea.trim()) payload.initial_idea = initialIdea.trim();
        if (businessId) payload.business_id = businessId;
        const res = await chatApi.start(payload);
        setConversationId(res.conversation_id);
        if (res.context) {
          setContext(res.context as ExtractedBrandContext);
        }

        const initialMsgs: ChatMessageItem[] = [];
        if (initialIdea && initialIdea.trim()) {
          initialMsgs.push({
            id: `init-user-${Date.now()}`,
            role: "customer",
            content: initialIdea.trim(),
            createdAt: new Date().toISOString(),
          });
        }
        if (res.greeting_message) {
          initialMsgs.push({
            id: `init-abija-${Date.now()}`,
            role: "assistant",
            content: res.greeting_message,
            createdAt: new Date().toISOString(),
          });
        }
        setMessages(initialMsgs);
        setIsThinking(false);
        return res;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to start conversation";
        setError(msg);
        setIsThinking(false);
        return null;
      }
    },
    []
  );

  // Send a message over WebSocket
  const sendMessage = useCallback(
    (text: string) => {
      const clean = text.trim();
      if (!clean) return;

      const userMsg: ChatMessageItem = {
        id: `user-${Date.now()}`,
        role: "customer",
        content: clean,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsThinking(true);
      setError(null);
      streamingAccRef.current = "";
      setStreamingContent("");

      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ content: clean }));
      } else {
        setError("Disconnected from chat. Please check your connection.");
        setIsThinking(false);
      }
    },
    []
  );

  // Load past history
  const loadHistory = useCallback(async (convId: string) => {
    try {
      const data = await chatApi.history(convId);
      setConversationId(convId);
      if (data.context) {
        setContext(data.context as ExtractedBrandContext);
      }
      if (data.messages && data.messages.length > 0) {
        setMessages(
          data.messages.map((m: ChatMessage) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            createdAt: m.created_at,
          }))
        );
      }
    } catch (err: unknown) {
      console.warn("Could not load chat history", err);
    }
  }, []);

  return {
    conversationId,
    messages,
    streamingContent,
    context,
    isConnected,
    isThinking,
    error,
    startConversation,
    sendMessage,
    loadHistory,
    setContext,
  };
}
