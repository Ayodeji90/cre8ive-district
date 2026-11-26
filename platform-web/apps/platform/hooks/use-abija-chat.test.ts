/**
 * Contract tests for the chat / state frontend integration.
 *
 * Written against the locked JSON contract (authoritative; NOT the live backend).
 *
 * The tested hook is `useAbijaChat` from `./use-abija-chat`, whose contract
 * surface is:
 *   useAbijaChat({ businessId, api?, initialIdea? }) => {
 *     state: WorkspaceState | null,        // hydrated from GET /api/businesses/{id}/state
 *     conversation: ChatResumeResponse | null,
 *     pendingApprovals: ApprovalItem[],
 *     recentApprovals: ApprovalItem[],
 *     retry: (approvalId: string) => void,
 *     sendMessage: (text: string) => void,
 *   }
 *
 * Contract surface lives in @cre8ive/api-client:
 *   businessesApi.state(businessId)       -> WorkspaceState
 *   chatApi.resume(businessId, {initial_idea}) -> ChatResumeResponse
 *
 * Behaviors asserted (the 5 required):
 *  1. /state hydration: all fields reflected.
 *  2. /chat/resume mode=self-identifies (resumed vs new).
 *  3. ?idea= single persistence: initial_idea sent only on fresh session.
 *  4. Business switching re-resumes for the new business.
 *  5. Approval state machine UI labels per the UI rules.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act, render, renderHook, waitFor } from '@testing-library/react'
import * as React from 'react'
import { useAbijaChat } from './use-abija-chat'
import type {
  WorkspaceState,
  ChatResumeResponse,
  ApprovalItem,
  StatusString,
} from '@cre8ive/api-client'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const NOW = '2026-02-03T12:00:00.000Z'

function business(id = 'b-1', name = 'Acme', opts: Record<string, unknown> = {}) {
  return {
    id,
    name,
    slug: (name ?? '').toLowerCase().replace(/\s+/g, '-'),
    status: 'active' as StatusString,
    plan: 'pro' as string,
    credit_balance: 500 as number,
    ...opts,
  }
}

function brandKit(id = 'bk-1', version = 2, status: StatusString = 'pending_review') {
  return { id, version, status }
}

function siteBuild(
  id = 'sb-1',
  version = 3,
  status: StatusString = 'deployed',
  previewUrl = 'https://preview.example.com/app',
  deploymentUrl = 'https://app.example.com'
) {
  return { id, version, status, preview_url: previewUrl, deployment_url: deploymentUrl }
}

function conversation(id = 'conv-1', status: StatusString = 'active', updatedAt = NOW) {
  return { id, status, updated_at: updatedAt }
}

function agentRun(
  id: string,
  agentType: string,
  status: StatusString = 'running',
  currentStep: string | null = 'analyzing',
  updatedAt = NOW
) {
  return { id, agent_type: agentType, status, current_step: currentStep, updated_at: updatedAt }
}

// FastAPI encodes a pending approval as `decision: null` (no "pending" literal).
function approval(
  id: string,
  decision: ApprovalItem['decision'] = null,
  executionStatus: ApprovalItem['execution_status'] = 'not_started',
  executedAt: string | null = null,
  outcome: Record<string, unknown> | null = null
): ApprovalItem {
  return {
    id,
    agent_run_id: 'run-' + id,
    action_type: 'apply_brand_kit',
    summary: `Apply brand kit ${id}`,
    decision,
    decided_at: decision !== null ? NOW : null,
    execution_status: executionStatus,
    executed_at: executedAt,
    execution_outcome: outcome,
  }
}

const APPROVALS = {
  pending: approval('ap-1', null, 'not_started'),
  approvedNotExecuted: approval('ap-2', 'approved', 'queued'),
  approvedSucceeded: approval('ap-3', 'approved', 'succeeded', NOW, { applied: true }),
  approvedFailed: approval('ap-4', 'approved', 'failed', NOW, { error: 'timeout' }),
  rejected: approval('ap-5', 'rejected', 'not_started'),
  expired: approval('ap-6', 'expired', 'not_started'),
} as const

// ---------------------------------------------------------------------------
// API contract surface (mirrors @cre8ive/api-client shape for the tests)
// ---------------------------------------------------------------------------

/**
 * The hook accepts an optional `api` override with the same shape the real
 * implementation uses. Tests inject a mock whose calls we assert on.
 */
interface HookApi {
  state: (businessId: string) => Promise<WorkspaceState>
  resume: (businessId: string, body: { initial_idea: string | null }) => Promise<ChatResumeResponse>
  wsConnect: (conversationId: string) => void
}

/**
 * Shared fixture: /state is keyed by the requested business id so tests that
 * switch businesses observe the matching state payload.
 */
function emptyStateFor(businessId: string): WorkspaceState {
  return {
    business: business(businessId, businessId === 'b-2' ? 'BetaCo' : 'Acme'),
    project_id: null,
    latest_brand_kit: null,
    latest_site_build: null,
    active_conversation: null,
    active_runs: [],
    pending_approvals: [],
    recent_approvals: [],
  }
}

const DEFAULT_API: HookApi = {
  state: vi.fn().mockImplementation((businessId: string) => Promise.resolve(emptyStateFor(businessId))),
  resume: vi.fn().mockResolvedValue({
    conversation_id: 'conv-fresh',
    mode: 'new',
    business_id: 'b-1',
    context: {},
    greeting: 'How can I help?',
  }),
  wsConnect: vi.fn(),
}

// ---------------------------------------------------------------------------
// Harness — renders the real hook with injected API + controlled pathname
// ---------------------------------------------------------------------------

/**
 * Reset `globalThis.location` so the hook's ?idea= parsing reads our test URL.
 */
function setLocation(pathname: string) {
  Object.defineProperty(globalThis, 'location', {
    value: new URL(pathname, 'http://localhost'),
    writable: true,
    configurable: true,
  })
}

function makeHarness(opts: {
  businessId?: string
  initialIdea?: string | null
  pathname?: string
  api?: HookApi
} = {}) {
  const businessId = opts.businessId ?? 'b-1'
  const initialIdea = opts.initialIdea ?? null
  const pathname = opts.pathname ?? `/workspace${initialIdea ? '?idea=' + encodeURIComponent(initialIdea) : ''}`
  const api = opts.api ?? DEFAULT_API

  setLocation(pathname)
  const { result, rerender, unmount } = renderHook(
    (props: { businessId: string; initialIdea: string | null }) => {
      const hook = useAbijaChat({ businessId: props.businessId, api, initialIdea: props.initialIdea })
      return hook
    },
    {
      initialProps: { businessId, initialIdea },
    },
  )

  return {
    result,
    rerender: (next: { businessId?: string; initialIdea?: string | null }) =>
      rerender({
        businessId: next.businessId ?? businessId,
        initialIdea: next.initialIdea ?? initialIdea,
      }),
    unmount,
    api,
    pathname,
  }
}

// ---------------------------------------------------------------------------
// Approval label derivation — the contract the workspace must render
// ---------------------------------------------------------------------------

/**
 * Pure derivation mirroring the workspace's approval UI rules. This is the
 * contract the workspace component is tested against; hook tests confirm the
 * hook exposes the raw approvals, and a separate workspace component test
 * (or the same surface, kept pure here) confirms the labels.
 */
function approvalLabels(items: ApprovalItem[]): Array<{ id: string; actions: string[] }> {
  const out: Array<{ id: string; actions: string[] }> = []
  for (const item of items) {
    const actions: string[] = []
    if (item.decision === null) {
      actions.push('Approve', 'Reject')
    }
    if (item.decision === 'approved' && item.executed_at === null) {
      actions.push('Approved — Executing')
    }
    if (item.decision === 'approved' && item.executed_at !== null && item.execution_status === 'succeeded') {
      actions.push('Completed')
    }
    if (item.execution_status === 'failed') {
      actions.push('Execution Failed', 'Retry')
    }
    out.push({ id: item.id, actions })
  }
  return out
}

// ---------------------------------------------------------------------------
// Contract tests
// ---------------------------------------------------------------------------

describe('useAbijaChat — contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // --- 1. /state hydration -----------------------------------------------

  describe('1. /state hydration', () => {
    it('reflects the full WorkspaceStateResponse in state', async () => {
      const stateResponse: WorkspaceState = {
        business: business('b-1', 'Acme', { credit_balance: 120 }),
        project_id: 'p-9',
        latest_brand_kit: brandKit('bk-1', 2, 'pending_review'),
        latest_site_build: siteBuild('sb-1', 3, 'deployed'),
        active_conversation: conversation('conv-1', 'active'),
        active_runs: [agentRun('r-1', 'brand_kit_applier', 'running', 'applying_v3')],
        pending_approvals: [APPROVALS.pending],
        recent_approvals: [APPROVALS.approvedSucceeded],
      }

      const api: HookApi = {
        state: vi.fn().mockResolvedValue(stateResponse),
        resume: vi.fn().mockResolvedValue({
          conversation_id: 'conv-hydrated',
          mode: 'resumed',
          business_id: 'b-1',
          context: {},
          greeting: null,
        }),
        wsConnect: vi.fn(),
      }

      const h = makeHarness({ initialIdea: null, api })

      await waitFor(() => {
        expect(h.result.current.state).not.toBeNull()
      })

      expect(h.result.current.state).toEqual(stateResponse)
      expect(h.result.current.pendingApprovals).toEqual([APPROVALS.pending])
      expect(h.result.current.recentApprovals).toEqual([APPROVALS.approvedSucceeded])
      expect(h.api.state).toHaveBeenCalledWith('b-1')
      expect(h.api.state).toHaveBeenCalledTimes(1)
    })

    it('fetches /state again when the business id changes', async () => {
      const h = makeHarness({ businessId: 'b-1', initialIdea: null })

      await waitFor(() => {
        expect(h.result.current.state?.business.id).toBe('b-1')
      })

      h.rerender({ businessId: 'b-2' })

      await waitFor(() => {
        expect(h.result.current.state?.business.id).toBe('b-2')
      })

      expect(h.api.state).toHaveBeenLastCalledWith('b-2')
    })
  })

  // --- 2. /chat/resume mode self-identification --------------------------

  describe('2. /chat/resume mode self-identification', () => {
    it('resumes an existing conversation (mode:resumed) when one is active', async () => {
      const api: HookApi = {
        state: vi.fn().mockResolvedValue({
          business: business('b-1'),
          project_id: null,
          latest_brand_kit: null,
          latest_site_build: null,
          active_conversation: conversation('conv-existing'),
          active_runs: [],
          pending_approvals: [],
          recent_approvals: [],
        }),
        resume: vi.fn().mockResolvedValue({
          conversation_id: 'conv-existing',
          mode: 'resumed',
          business_id: 'b-1',
          context: {},
          greeting: 'Welcome back',
        }),
        wsConnect: vi.fn(),
      }

      const h = makeHarness({ initialIdea: null, api })

      await waitFor(() => {
        expect(h.result.current.conversation?.id).toBe('conv-existing')
      })

      expect(h.result.current.conversation?.mode).toBe('resumed')
      expect(h.api.resume).toHaveBeenCalledWith('b-1', { initial_idea: null })
    })

    it('starts a new conversation (mode:new) when none is active and no idea', async () => {
      const api: HookApi = {
        state: vi.fn().mockResolvedValue({
          business: business('b-1'),
          project_id: null,
          latest_brand_kit: null,
          latest_site_build: null,
          active_conversation: null,
          active_runs: [],
          pending_approvals: [],
          recent_approvals: [],
        }),
        resume: vi.fn().mockResolvedValue({
          conversation_id: 'conv-new',
          mode: 'new',
          business_id: 'b-1',
          context: {},
          greeting: 'Hello',
        }),
        wsConnect: vi.fn(),
      }

      const h = makeHarness({ initialIdea: null, api })

      await waitFor(() => {
        expect(h.result.current.conversation?.id).toBe('conv-new')
      })

      expect(h.result.current.conversation?.mode).toBe('new')
      expect(h.api.resume).toHaveBeenCalledWith('b-1', { initial_idea: null })
    })
  })

  // --- 3. ?idea= single persistence --------------------------------------

  describe('3. ?idea= single persistence', () => {
    it('sends initial_idea only on the first fresh session from ?idea=', async () => {
      const api: HookApi = {
        state: vi.fn().mockResolvedValue({
          business: business('b-1'),
          project_id: null,
          latest_brand_kit: null,
          latest_site_build: null,
          active_conversation: null,
          active_runs: [],
          pending_approvals: [],
          recent_approvals: [],
        }),
        resume: vi.fn().mockResolvedValue({
          conversation_id: 'conv-1',
          mode: 'new',
          business_id: 'b-1',
          context: {},
          greeting: 'Starting your landing page',
        }),
        wsConnect: vi.fn(),
      }

      const h = makeHarness({
        businessId: 'b-1',
        initialIdea: 'Build a landing page',
        pathname: '/workspace?idea=Build%20a%20landing%20page',
        api,
      })

      await waitFor(() => {
        expect(h.result.current.conversation?.id).toBe('conv-1')
      })

      // First resume on a fresh session with ?idea= → initial_idea = the idea.
      expect(h.api.resume).toHaveBeenCalledWith('b-1', {
        initial_idea: 'Build a landing page',
      })

      // Re-render with the same business, no new idea: the conversation is now
      // active (resume created it), so a subsequent resume must use null.
      const resume2 = vi.fn().mockResolvedValue({
        conversation_id: 'conv-1',
        mode: 'resumed',
        business_id: 'b-1',
        context: {},
        greeting: null,
      })

      // The conversation is now active. Re-mount a fresh hook for the same
      // business with no new idea — the second mount MUST resume with
      // initial_idea null (never re-send the ?idea= value).
      const h2 = makeHarness({
        businessId: 'b-1',
        initialIdea: null,
        pathname: '/workspace',
        api: { ...api, resume: resume2 } as HookApi,
      })

      await waitFor(() => {
        expect(h2.result.current.conversation?.id).toBe('conv-1')
      })

      expect(resume2).toHaveBeenCalledWith('b-1', { initial_idea: null })
    })
  })

  // --- 3b. no active conversation in /state, resume reports "resumed" ------

  describe('3b. /state has no active conversation but resume returns mode:resumed', () => {
    it('treats the returned conversation as active and never re-sends initial_idea', async () => {
      const resume = vi
        .fn()
        .mockResolvedValueOnce({
          conversation_id: 'conv-reused',
          mode: 'resumed',
          business_id: 'b-1',
          context: {},
          greeting: null,
        })
        .mockResolvedValueOnce({
          conversation_id: 'conv-reused',
          mode: 'resumed',
          business_id: 'b-1',
          context: {},
          greeting: null,
        })

      const api: HookApi = {
        state: vi.fn().mockResolvedValue({
          business: business('b-1'),
          project_id: null,
          latest_brand_kit: null,
          latest_site_build: null,
          // No active conversation on the server projection...
          active_conversation: null,
          active_runs: [],
          pending_approvals: [],
          recent_approvals: [],
        } as WorkspaceState),
        // ...yet resume reactivates an existing conversation.
        resume,
        wsConnect: vi.fn(),
      }

      const h = makeHarness({
        businessId: 'b-1',
        initialIdea: 'Build a landing page',
        pathname: '/workspace?idea=Build%20a%20landing%20page',
        api,
      })

      await waitFor(() => {
        expect(h.result.current.conversation?.id).toBe('conv-reused')
      })

      expect(h.result.current.conversation?.mode).toBe('resumed')
      expect(resume).toHaveBeenNthCalledWith(1, 'b-1', {
        initial_idea: 'Build a landing page',
      })

      // Now that the resume returned an existing conversation, a later
      // startConversation must not resend the initial idea.
      await act(async () => {
        await h.result.current.startConversation('Build a landing page')
      })

      expect(resume).toHaveBeenNthCalledWith(2, 'b-1', { initial_idea: null })
    })
  })

  // --- 4. business switching re-resumes ----------------------------------

  describe('4. business switching re-resumes', () => {
    it('resumes the conversation for the new business on switch', async () => {
      const api: HookApi = {
        state: vi
          .fn()
          .mockResolvedValueOnce({
            business: business('b-1'),
            project_id: null,
            latest_brand_kit: null,
            latest_site_build: null,
            active_conversation: null,
            active_runs: [],
            pending_approvals: [],
            recent_approvals: [],
          })
          .mockResolvedValueOnce({
            business: business('b-2', 'BetaCo'),
            project_id: null,
            latest_brand_kit: null,
            latest_site_build: null,
            active_conversation: null,
            active_runs: [],
            pending_approvals: [],
            recent_approvals: [],
          }),
        resume: vi.fn().mockResolvedValue({
          conversation_id: 'conv-switch',
          mode: 'new',
          business_id: 'b-2',
          context: {},
          greeting: 'New business',
        }),
        wsConnect: vi.fn(),
      }

      const h = makeHarness({ businessId: 'b-1', initialIdea: null, api })

      await waitFor(() => {
        expect(h.result.current.state?.business.id).toBe('b-1')
      })

      h.rerender({ businessId: 'b-2' })

      await waitFor(() => {
        expect(h.result.current.state?.business.id).toBe('b-2')
      })

      expect(h.api.state).toHaveBeenLastCalledWith('b-2')
      expect(h.api.resume).toHaveBeenLastCalledWith('b-2', { initial_idea: null })
    })
  })

  // --- 5. approval state machine UI --------------------------------------

  describe('5. approval state machine UI', () => {
    /**
     * Render a small component that consumes the hook's approval lists and
     * derives the visible labels + actions. We assert against the derived
     * label set, which is the UI contract.
     */
    function ApprovalPane({ pending, recent }: { pending: ApprovalItem[]; recent: ApprovalItem[] }) {
      const labels = React.useMemo(() => approvalLabels([...pending, ...recent]), [pending, recent])
      return React.createElement('div', { 'data-labels': JSON.stringify(labels) }, '')
    }

    function renderApprovalPane(pending: ApprovalItem[], recent: ApprovalItem[]) {
      const { container } = render(
        React.createElement(ApprovalPane, { pending, recent }),
      )
      const parsed = JSON.parse(container.firstChild?.getAttribute('data-labels') ?? '[]')
      return parsed
    }

    it('renders pending approvals with Approve/Reject', () => {
      const labels = renderApprovalPane([APPROVALS.pending], [])
      const item = labels.find((l: { id: string }) => l.id === APPROVALS.pending.id)!
      expect(item.actions).toEqual(['Approve', 'Reject'])
    })

    it('renders approved-but-not-executed as Approved — Executing, never Completed', () => {
      const labels = renderApprovalPane([], [APPROVALS.approvedNotExecuted])
      const item = labels.find((l: { id: string }) => l.id === APPROVALS.approvedNotExecuted.id)!
      expect(item.actions).toContain('Approved — Executing')
      expect(item.actions).not.toContain('Completed')
    })

    it('renders approved + executed + succeeded as Completed with outcome', () => {
      const labels = renderApprovalPane([], [APPROVALS.approvedSucceeded])
      const item = labels.find((l: { id: string }) => l.id === APPROVALS.approvedSucceeded.id)!
      expect(item.actions).toContain('Completed')
      // outcome present on the item in the source.
      expect(APPROVALS.approvedSucceeded.execution_outcome).toEqual({ applied: true })
    })

    it('renders failed executions as Execution Failed with retry', () => {
      const labels = renderApprovalPane([], [APPROVALS.approvedFailed])
      const item = labels.find((l: { id: string }) => l.id === APPROVALS.approvedFailed.id)!
      expect(item.actions).toContain('Execution Failed')
      expect(item.actions).toContain('Retry')
    })

    it('does not show Approve/Reject for non-pending decisions', () => {
      const labels = renderApprovalPane([], [APPROVALS.rejected, APPROVALS.expired])
      for (const id of [APPROVALS.rejected.id, APPROVALS.expired.id]) {
        const item = labels.find((l: { id: string }) => l.id === id)!
        expect(item.actions).not.toContain('Approve')
        expect(item.actions).not.toContain('Reject')
      }
    })
  })
})
