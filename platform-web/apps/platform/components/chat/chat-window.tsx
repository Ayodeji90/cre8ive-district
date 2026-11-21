"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { AbijaAvatar } from "./abija-avatar";
import { ChatStageStepper } from "./chat-stage-stepper";
import { QuickActions } from "./quick-actions";
import type { ChatMessageItem, ExtractedBrandContext } from "../../hooks/use-abija-chat";

interface ChatWindowProps {
  messages: ChatMessageItem[];
  streamingContent: string;
  context: ExtractedBrandContext;
  isThinking: boolean;
  isConnected: boolean;
  error: string | null;
  onSendMessage: (text: string) => void;
  onRestartChat?: () => void;
}

export function ChatWindow({
  messages,
  streamingContent,
  context,
  isThinking,
  isConnected,
  error,
  onSendMessage,
}: ChatWindowProps) {
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages or streaming chunks
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, isThinking]);

  const handleSend = () => {
    if (!inputText.trim() || isThinking) return;
    onSendMessage(inputText);
    setInputText("");
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="flex h-full flex-col bg-[#FDFBF7]">
      {/* Stage Stepper Banner */}
      <ChatStageStepper context={context} />

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 space-y-5">
        {messages.length === 0 && !streamingContent && !isThinking && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12 px-4">
            <AbijaAvatar size="lg" />
            <h3 className="mt-4 text-xl font-bold text-charcoal">Meet Abija</h3>
            <p className="mt-2 max-w-sm text-sm text-grey-600">
              Your AI brand co-founder. Share your business idea and Abija will shape your brand,
              visuals, and high-converting website.
            </p>
          </div>
        )}

        {messages.map((msg) => {
          const isAbija = msg.role === "assistant";
          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${isAbija ? "justify-start" : "justify-end"}`}
            >
              {isAbija && <AbijaAvatar size="sm" className="mt-0.5" />}
              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-2xs ${
                  isAbija
                    ? "bg-white text-charcoal border border-grey-150 rounded-tl-sm"
                    : "bg-charcoal text-white rounded-tr-sm"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <span
                  className={`mt-1.5 block text-[10px] ${
                    isAbija ? "text-grey-600" : "text-grey-400"
                  }`}
                >
                  {isAbija ? "Abija" : "You"}
                </span>
              </div>
            </div>
          );
        })}

        {/* Live Streaming Assistant Message */}
        {(streamingContent || isThinking) && (
          <div className="flex items-start gap-3 justify-start">
            <AbijaAvatar isThinking={isThinking} size="sm" className="mt-0.5" />
            <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tl-sm bg-white text-charcoal border border-grey-150 px-4 py-3 text-sm leading-relaxed shadow-2xs">
              {streamingContent ? (
                <div className="whitespace-pre-wrap">
                  {streamingContent}
                  <span className="inline-block w-1.5 h-4 ml-0.5 bg-orange animate-pulse" />
                </div>
              ) : (
                <div className="flex items-center gap-1.5 py-1">
                  <span className="size-2 rounded-full bg-orange animate-bounce [animation-delay:-0.3s]" />
                  <span className="size-2 rounded-full bg-orange animate-bounce [animation-delay:-0.15s]" />
                  <span className="size-2 rounded-full bg-orange animate-bounce" />
                </div>
              )}
              <span className="mt-1.5 block text-[10px] text-grey-600">Abija</span>
            </div>
          </div>
        )}

        {/* Error notification */}
        {error && (
          <div className="mx-auto max-w-md rounded-xl bg-red-50 border border-red-200 p-3 text-center text-xs text-red-700">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Tray & Quick Actions */}
      <div className="border-t border-grey-200 bg-white p-3 sm:p-4">
        <div className="max-w-3xl mx-auto">
          {/* Quick Action Chips */}
          <QuickActions
            context={context}
            onSelect={(actionText) => onSendMessage(actionText)}
            disabled={isThinking}
          />

          {/* Text Input Row */}
          <div className="mt-2 relative flex items-end gap-2 rounded-2xl border border-grey-200 bg-white p-2 shadow-2xs focus-within:border-orange focus-within:ring-2 focus-within:ring-orange/20 transition-all">
            <textarea
              ref={inputRef}
              rows={1}
              value={inputText}
              onChange={handleTextareaInput}
              onKeyDown={handleKeyDown}
              placeholder={
                isConnected
                  ? "Type your answer or business idea..."
                  : "Connecting to Abija..."
              }
              className="flex-1 max-h-32 resize-none bg-transparent px-2 py-1 text-sm text-charcoal placeholder:text-grey-400 focus:outline-none"
            />
            <button
              type="button"
              disabled={!inputText.trim() || isThinking}
              onClick={handleSend}
              className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-orange text-white hover:bg-orange-hover active:scale-95 disabled:pointer-events-none disabled:opacity-40 transition-all shadow-xs"
              aria-label="Send message to Abija"
            >
              <svg
                viewBox="0 0 20 20"
                fill="currentColor"
                className="size-4 rotate-90 transform translate-x-0.5"
              >
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
          <div className="mt-1 flex items-center justify-between px-1 text-[11px] text-grey-600">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span className="flex items-center gap-1">
              <span
                className={`size-1.5 rounded-full ${
                  isConnected ? "bg-emerald-500" : "bg-amber-500"
                }`}
              />
              {isConnected ? "Connected" : "Reconnecting"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
