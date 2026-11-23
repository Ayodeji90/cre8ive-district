"use client"

import * as React from 'react'
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  chatApi,
  businessesApi,
  type ChatResumeRequest,
  type ChatResumeResponse,
  type WorkspaceState,
  type ApprovalItem,
} from '@cre8ive/api-client'

// ---------------------------------------------------------------------------
// Legacy re-exports (kept for downstream chat components; do not remove)
// ---------------------------------------------------------------------------

export interface ChatMessageItem {
  id: string
  role: 'customer' | 'assistant' | 'system'
  content: string
  createdAt: string
  isStreaming?: boolean
}

export interface ExtractedBrandContext {
  conversation_stage?: string
  business_name?: string
  description?: string
  industry?: string
  target_audience?: string
  style_keywords?: string[]
  mood?: string
  ready_to_generate?: boolean
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Public hook contract
// ---------------------------------------------------------------------------

export interface UseAbijaChatOptions {
  /** The business whose workspace state + chat to drive. Required. */
  businessId: string
  /** Optional API override for tests. When omitted, uses the real @cre8ive/api-client. */
  api?: {
    state: (businessId: string) => Promise<WorkspaceState>
    resume: (businessId: string, body: ChatResumeRequest) => Promise<ChatResumeResponse>
    wsConnect: (conversationId: string) => void
  }
  /**
   * Initial idea for a fresh session. When provided (including via ?idea= parsed
   * from the URL by the caller), it is sent as `initial_idea` ONLY on the first
   * resume of a fresh session (no active_conversation). On resume / business switch
   * it is sent as null.
   */
  initialIdea?: string | null
}

/** The resume response normalized with a convenient `id` alias. */
export interface AbijaConversation extends ChatResumeResponse {
  id: string
}

export interface UseAbijaChatReturn {
  /** Hydration from GET /api/businesses/{id}/state, or null before the first fetch. */
  state: WorkspaceState | null
  /** The resume response for the active conversation, or null. */
  conversation: AbijaConversation | null
  /** Pending approvals from the workspace state. */
  pendingApprovals: ApprovalItem[]
  /** Recent approvals from the workspace state. */
  recentApprovals: ApprovalItem[]
  /** Retry a failed approval execution by id. */
  retry: (approvalId: string) => void
  /** Send a chat message over the WebSocket (legacy-compat shim). */
  sendMessage: (text: string) => void

  // ---- Legacy return fields (deprecated; workspace rewrite will drop these) ----
  messages: ChatMessageItem[]
  streamingContent: string
  context: ExtractedBrandContext
  isThinking: boolean
  isConnected: boolean
  error: string | null
  startConversation: (initialIdea?: string, businessId?: string) => Promise<ChatResumeResponse | null>
  loadHistory: (convId: string) => Promise<void>
  setContext: (ctx: ExtractedBrandContext) => void
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAbijaChat(opts: UseAbijaChatOptions): UseAbijaChatReturn {
  const { businessId, api, initialIdea: explicitIdea } = opts

  // Memoized so the load effect below does not re-fire on every render when no
  // test override is provided.
  const apiLayer = React.useMemo(
    () =>
      api ?? {
        state: (id: string) => businessesApi.state(id),
        resume: (id: string, body: ChatResumeRequest) => chatApi.resume(id, body),
        wsConnect: (conversationId: string) => {
          // In the real app the workspace connects the WS via a separate
          // provider; the workspace owns the WebSocket lifecycle.
          void conversationId
        },
      },
    [api],
  )

  const [state, setState] = useState<WorkspaceState | null>(null)
  const [conversation, setConversation] = useState<AbijaConversation | null>(null)
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalItem[]>([])
  const [recentApprovals, setRecentApprovals] = useState<ApprovalItem[]>([])
  // The retry flag itself is not read yet; the workspace surfaces retry from
  // the approval's execution_status, so only the setter is used.
  const [, setFailedApprovalIds] = useState<Set<string>>(new Set())

  // Track whether we have already performed the first resume for this
  // businessId + initialIdea combination. This ensures initial_idea is sent
  // exactly once on a fresh session.
  const firstResumeDoneRef = useRef<boolean>(false)
  const lastBusinessIdRef = useRef<string | null>(null)
  const activeConversationIdRef = useRef<string | null>(null)

  // Reset the "first resume" flag when the business changes or the explicit
  // idea changes to a fresh value.
  useEffect(() => {
    // Treat a new business as a fresh start regardless of idea.
    const businessChanged = lastBusinessIdRef.current !== null && lastBusinessIdRef.current !== businessId
    if (businessId === lastBusinessIdRef.current && !businessChanged) {
      return
    }
    lastBusinessIdRef.current = businessId
    firstResumeDoneRef.current = false
    activeConversationIdRef.current = null
  }, [businessId, explicitIdea])

  // Ordered load: GET /state  →  POST /chat/resume  →  (WS connect is owned
  // by the workspace; we call api.wsConnect here for testability only).
  useEffect(() => {
    if (!businessId) return

    let cancelled = false

    async function load() {
      // 1. Hydrate workspace state.
      const ws: WorkspaceState = await apiLayer.state(businessId)
      if (cancelled) return
      setState(ws)
      setPendingApprovals(ws.pending_approvals)
      setRecentApprovals(ws.recent_approvals)

      const hasActiveConversation = ws.active_conversation != null

      // Track the active conversation id from state so we can decide whether
      // the next resume is "fresh" even if the backend hasn't created it yet.
      if (ws.active_conversation) {
        activeConversationIdRef.current = ws.active_conversation.id
      }

      // 2. Decide the initial_idea payload.
      //
      // initial_idea is sent ONLY when:
      //   - this is the first resume for this business+idea combo (firstResumeDoneRef false), AND
      //   - there is no active conversation (fresh session), AND
      //   - we have an idea to send (explicitIdea parsed from ?idea=, or passed in).
      //
      // Otherwise initial_idea is null.
      const shouldSendIdea =
        !firstResumeDoneRef.current &&
        !hasActiveConversation &&
        explicitIdea != null &&
        explicitIdea.trim().length > 0

      const initialIdeaPayload: string | null =
        shouldSendIdea ? explicitIdea.trim() : null

      // Mark the first resume as done for this business+idea so subsequent
      // resumes (re-mount, reconnect, business switch) never re-send the idea.
      firstResumeDoneRef.current = true

      // 3. Resume / start the chat session.
      const res: ChatResumeResponse = await apiLayer.resume(businessId, {
        initial_idea: initialIdeaPayload,
      })
      if (cancelled) return

      setConversation({ ...res, id: res.conversation_id })
      if (res.conversation_id) {
        activeConversationIdRef.current = res.conversation_id
        apiLayer.wsConnect(res.conversation_id)
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [businessId, explicitIdea, apiLayer])

  // Reset first-resume flag when the explicit idea changes to a new non-empty
  // value while the business is the same — this allows ?idea= editing to
  // re-trigger a fresh-session send only if there's still no active
  // conversation. In practice the workspace passes the idea once; this branch
  // is a safety net.
  useEffect(() => {
    if (explicitIdea == null || explicitIdea.trim().length === 0) return
    // Only reset if we have no active conversation right now.
    if (activeConversationIdRef.current == null) {
      firstResumeDoneRef.current = false
    }
  }, [explicitIdea])

  const retry = useCallback(
    (approvalId: string) => {
      setFailedApprovalIds((prev) => new Set(prev).add(approvalId))
      // The real retry hits a separate approve/reject endpoint; here we raise
      // the flag so the workspace can surface a retry affordance. The actual
      // HTTP call lives in the workspace action handlers.
    },
    [],
  )

  // Legacy chat-stream fields derived from the resume response / state.
  // The workspace currently renders these; the rewrite will switch to the
  // conversation greeting + WS-driven messages instead.
  const messages: ChatMessageItem[] = React.useMemo(() => {
    const list: ChatMessageItem[] = []
    if (conversation?.greeting) {
      list.push({
        id: `init-abija-${conversation.conversation_id}`,
        role: 'assistant',
        content: conversation.greeting,
        createdAt: new Date().toISOString(),
        isStreaming: false,
      })
    }
    return list
  }, [conversation])

  const streamingContent = React.useMemo(() => '', [])
  const context: ExtractedBrandContext = React.useMemo(
    () => ({
      conversation_stage: 'greeting',
      business_name: state?.business?.name ?? undefined,
      ready_to_generate: false,
      ...(conversation?.context ?? {}),
    }),
    [state?.business?.name, conversation?.context],
  )
  const isThinking = false
  const isConnected = conversation != null
  const error: string | null = null

  const startConversation = useCallback(
    async (initialIdea?: string, businessId?: string): Promise<ChatResumeResponse | null> => {
      // Legacy compat: delegate to resume for the current business. When an
      // explicit business id is supplied we only use it to decide the idea
      // payload; the hook itself is already keyed to opts.businessId.
      const targetBusiness = businessId ?? opts.businessId
      // Never re-send an initial idea once a conversation already exists
      // (including when a fresh /state + resume returned an existing one).
      const alreadyActive =
        activeConversationIdRef.current != null || conversation != null
      const idea =
        !alreadyActive && initialIdea?.trim().length ? initialIdea.trim() : null
      try {
        const res = await apiLayer.resume(targetBusiness, { initial_idea: idea ?? null })
        setConversation({ ...res, id: res.conversation_id })
        if (res.conversation_id) {
          activeConversationIdRef.current = res.conversation_id
          apiLayer.wsConnect(res.conversation_id)
        }
        return res
      } catch {
        return null
      }
    },
    [apiLayer, opts.businessId, conversation],
  )

  const loadHistory = useCallback(async (convId: string) => {
    // Legacy compat: there is no separate history endpoint in the new contract.
    // Treat the active conversation as loaded.
    if (conversation?.conversation_id === convId) return
    // No-op in the new contract; the workspace should use state.active_conversation.
  }, [conversation?.conversation_id])

  const setContext = useCallback(() => {
    // Legacy compat shim; real context comes from the resume response + WS.
  }, [])

  const sendMessage = useCallback((text: string) => {
    // Legacy-compat shim: the real send path is owned by the workspace's
    // ChatWindow via the WebSocket provider.
    console.debug('[useAbijaChat] sendMessage shim:', text)
  }, [])

  return {
    state,
    conversation,
    pendingApprovals,
    recentApprovals,
    retry,
    sendMessage,
    messages,
    streamingContent,
    context,
    isThinking,
    isConnected,
    error,
    startConversation,
    loadHistory,
    setContext,
  }
}
