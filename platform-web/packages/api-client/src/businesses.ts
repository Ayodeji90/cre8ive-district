import type { Business, BusinessCreate, BusinessUpdate } from '@cre8ive/types'
import { apiClient } from './client'

export type { Business, BusinessCreate, BusinessUpdate }

// ---------------------------------------------------------------------------
// Workspace state — mirrors GET /api/businesses/{business_id}/state response
// ---------------------------------------------------------------------------

/** Status enum-ish strings used across workspace fields. */
export type StatusString = string

/**
 * Approval item from the workspace state (`ApprovalItemResponse`).
 *
 * FastAPI encodes a *pending* approval as `decision: null` — there is no
 * literal "pending" value. A null decision means it needs your OK.
 */
export interface ApprovalItem {
  id: string
  agent_run_id: string | null
  action_type: string
  summary: string
  decision: 'approved' | 'rejected' | 'expired' | null
  decided_at: string | null
  execution_status: 'not_started' | 'queued' | 'running' | 'succeeded' | 'failed'
  executed_at: string | null
  execution_outcome: Record<string, unknown> | null
}

/** An active agent run (`AgentRunResponse`). */
export interface AgentRun {
  id: string
  project_id: string
  user_id: string
  goal: string
  credits_budget: number
  credits_used: number
  max_iterations: number
  iteration_count: number
  status: StatusString
  result_summary: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
}

/** The latest brand kit (`BrandKitResponse`). */
export interface BrandSummary {
  id: string
  project_id: string
  version: number
  brand_name: string | null
  tagline: string | null
  palette_json: Record<string, unknown>
  typography_json: Record<string, unknown>
  logo_svg: string | null
  logo_urls: Array<Record<string, unknown>>
  strategy: Record<string, unknown>
  copy: Record<string, unknown>
  offer_tiers_json: Record<string, unknown>
  guidelines_pdf: string | null
  kit_zip_url: string | null
  status: StatusString
  created_at: string
  updated_at: string
}

/** The latest site build (`SiteBuildResponse`). */
export interface SiteBuildSummary {
  id: string
  project_id: string
  brand_kit_id: string | null
  version: number
  sandbox_id: string | null
  preview_url: string | null
  published_r2_path: string | null
  pages: Array<Record<string, unknown>>
  lighthouse: Record<string, unknown> | null
  build_status: StatusString
  build_error: string | null
  created_at: string
  updated_at: string
}

/** The latest brand projection (`BrandSummary`). */
export interface BrandProjection {
  id: string
  version: number
  status: StatusString
  strategy: Record<string, unknown>
  colors: Record<string, unknown>
  fonts: Record<string, unknown>
  logo_urls: unknown[]
  created_at: string
}

/** The latest website projection (`WebsiteSummary`). */
export interface WebsiteSummary {
  id: string
  status: StatusString
  deployment_url: string | null
  pages: Array<Record<string, unknown>>
  created_at: string
}

/** The active conversation summary (`ConversationSummary`). */
export interface ConversationSummary {
  id: string
  status: StatusString
  context: Record<string, unknown>
  created_at: string
  updated_at: string
}

/** Canonical business profile (`BusinessSummary`). */
export interface BusinessSummary {
  id: string
  name: string
  slug: string
  description: string | null
  industry: string | null
  location: string | null
  contact_phone: string | null
  contact_email: string | null
  plan: string
  credit_balance: number
  status: StatusString
  preferences: Record<string, unknown>
}

/** Full workspace state for a business (`WorkspaceStateResponse`). */
export interface WorkspaceState {
  business: BusinessSummary
  project_id: string | null
  latest_brand_kit: BrandSummary | null
  latest_site_build: SiteBuildSummary | null
  active_runs: AgentRun[]
  brand: BrandProjection | null
  website: WebsiteSummary | null
  active_conversation: ConversationSummary | null
  pending_approvals: ApprovalItem[]
  pending_approval_count: number
  recent_approvals: ApprovalItem[]
}

export const businessesApi = {
  list: () => apiClient.request<Business[]>('/api/businesses'),
  get: (id: string) => apiClient.request<Business>(`/api/businesses/${encodeURIComponent(id)}`),
  create: (data: BusinessCreate) =>
    apiClient.request<Business>('/api/businesses', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: string, data: BusinessUpdate) =>
    apiClient.request<Business>(`/api/businesses/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  /** GET /api/businesses/{business_id}/state */
  state: (businessId: string) =>
    apiClient.request<WorkspaceState>(`/api/businesses/${encodeURIComponent(businessId)}/state`),
}
