"use client"

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react"
import Link from "next/link"
import { signOut, useSession } from "next-auth/react"
import { useSearchParams } from "next/navigation"
import {
  billingApi,
  businessesApi,
  websitesApi,
  type Business,
  type ApprovalItem,
} from "@cre8ive/api-client"
import { useAbijaChat } from "../../hooks/use-abija-chat"
import { ChatWindow } from "../chat/chat-window"
import { BrandPreviewPane } from "../chat/brand-preview-pane"
import { TopUpModal } from "../billing/topup-modal"

interface AbijaWorkspaceProps {
  /** Legacy prop kept for backward compat with the workspace page; the hook is
  now driven by `businessId` + `?idea=` parsed from the URL. */
  initialIdea?: string
  /** Explicit business id to drive. When omitted, falls back to the session
  context's business id (backward compat). The hook itself is keyed to this
  value. */
  businessId?: string
}

export function AbijaWorkspace({ businessId: explicitBusinessId }: AbijaWorkspaceProps) {
  const { data: session, status: sessionStatus } = useSession()
  const searchParams = useSearchParams()
  const initialIdea = (searchParams?.get("idea")?.trim() ?? "") || undefined

  // Derive the driving business id: explicit prop wins, then session-context
  // legacy fallback, then null (no workspace).
  const sessionBusinessId =
    session?.accessToken
      ? (session as unknown as Record<string, unknown>).business_id as string | undefined | null
      : undefined
  const businessId = explicitBusinessId || sessionBusinessId || null

  // ---- workspace-local state (hydrated from useAbijaChat.state) ----
  const [mobileTab, setMobileTab] = useState<"chat" | "preview">("chat")
  const [isLaunching, setIsLaunching] = useState(false)
  const [isTopUpOpen, setIsTopUpOpen] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const switcherButtonRef = useRef<HTMLButtonElement>(null)
  const [reloadKey, setReloadKey] = useState(0)

  // Business switcher
  const [myBusinesses, setMyBusinesses] = useState<Business[]>([])
  const [isBusinessMenuOpen, setIsBusinessMenuOpen] = useState(false)
  const [isBusinessFormOpen, setIsBusinessFormOpen] = useState(false)
  const [newBusinessName, setNewBusinessName] = useState("")
  const [newBusinessIndustry, setNewBusinessIndustry] = useState("")
  const [businessFormError, setBusinessFormError] = useState<string | null>(null)
  const [isCreatingBusiness, setIsCreatingBusiness] = useState(false)

  // Website deployment tracking (legacy status text still shown in preview pane)
  const [deployedUrl, setDeployedUrl] = useState<string | null>(null)
  const [websiteStatus, setWebsiteStatus] = useState<string>("Drafting in Chat")
  const [websiteError, setWebsiteError] = useState<string | null>(null)
  const [websiteAttempts, setWebsiteAttempts] = useState(0)
  const [websiteLastAttempt, setWebsiteLastAttempt] = useState<string | null>(null)

  // ---- ordered load: /state → /chat/resume (initial_idea only on fresh) ----
  const {
    state,
    conversation,
    pendingApprovals,
    recentApprovals,
    retry,
    sendMessage,
  } = useAbijaChat({
    businessId: businessId ?? "",
    initialIdea: initialIdea || null,
  })

  // Hydration mirrors from state fed back into workspace locals so the preview
  // pane and credit badge keep working with the same shape they had before.
  const credits = state?.business?.credit_balance
  const currentBusiness = myBusinesses.find((b) => b.id === businessId)
  const businessName =
    state?.business?.name ??
    (((session?.user as unknown) as Record<string, unknown>).business_name as string | undefined) ??
    undefined

  // Sync live credit balance from billing API whenever business changes or on
  // reconnect, but prefer the value we got from /state if present.
  useEffect(() => {
    if (!businessId) return
    let cancelled = false
    billingApi
      .credits(businessId)
      .then((res) => {
        if (!cancelled && res?.balance !== undefined) {
          // Only refresh from the API if state hasn't already given us a fresh
          // value this cycle; the state.credit_balance is authoritative from the
          // workspace contract.
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadError("We couldn’t load your credit balance. Check your connection and try again.")
        }
      })
    return () => { cancelled = true }
  }, [businessId])

  // Website deployment status polling (legacy behaviour preserved).
  useEffect(() => {
    if (!businessId) return
    let cancelled = false
    const tick = () => {
      if (cancelled) return
      websitesApi
        .getStatus(businessId)
        .then((res) => {
          if (cancelled) return
          setWebsiteAttempts(res.attempt_count ?? 0)
          setWebsiteLastAttempt(res.last_attempt_at ?? null)
          if (res?.deployment_url && res.status === "deployed") {
            setDeployedUrl(res.deployment_url)
            setWebsiteStatus("Website Deployed & Live ✓")
            setWebsiteError(null)
          } else if (res?.status === "failed") {
            setWebsiteStatus("Website generation failed")
            setWebsiteError(res.last_error ?? "Website generation failed. Retry the job or contact support.")
          } else if (res?.status) {
            setWebsiteStatus(res.status === "failed" ? "Website generation failed" : `Website ${res.status}`)
            setWebsiteError(res.last_error ?? null)
          }
        })
        .catch(() => {
          if (!cancelled) setWebsiteError("Couldn’t check website status. We’ll keep trying.")
        })
    }
    tick()
    const timer = window.setInterval(tick, 2500)
    return () => { cancelled = true; window.clearInterval(timer) }
  }, [businessId])

  // Sync website status text from the state's latest_site_build / website
  // projection when available (FastAPI uses `build_status` + `published_r2_path`).
  useEffect(() => {
    const build = state?.latest_site_build
    const website = state?.website
    if (website?.deployment_url) {
      setDeployedUrl(website.deployment_url)
    } else if (build?.published_r2_path) {
      setDeployedUrl(build.published_r2_path)
    } else if (build?.preview_url) {
      setDeployedUrl(build.preview_url)
    }
    if (build) {
      if (build.build_status === "deployed") {
        setWebsiteStatus("Website Deployed & Live ✓")
      } else {
        setWebsiteStatus(`Website ${build.build_status}`)
      }
      setWebsiteError(build.build_error ?? null)
    } else if (website) {
      setWebsiteStatus(`Website ${website.status}`)
    }
  }, [state?.latest_site_build, state?.website])

  const refreshBusinesses = useCallback(() => {
    if (sessionStatus === "authenticated" && session?.user) {
      businessesApi
        .list()
        .then((list) => {
          if (Array.isArray(list)) setMyBusinesses(list)
        })
        .catch(() =>
          setLoadError("We couldn’t load your businesses. Check your connection and try again.")
        )
    }
  }, [session, sessionStatus])

  useEffect(() => {
    refreshBusinesses()
  }, [refreshBusinesses, businessId, reloadKey])

  // ---- approval labels (pure derivation, matches UI rules) ----
  // FastAPI encodes a pending approval as `decision: null` (no "pending" literal).
  function approvalLabel(item: ApprovalItem): string {
    if (item.decision === null) return "Needs Your OK"
    if (item.decision === "approved" && item.executed_at === null) return "Approved — Executing"
    if (item.decision === "approved" && item.executed_at != null && item.execution_status === "succeeded")
      return "Completed"
    if (item.decision === "approved" && item.execution_status === "failed") return "Execution Failed"
    if (item.decision === "rejected") return "Rejected"
    if (item.decision === "expired") return "Expired"
    return "Unknown"
  }

  function isActionable(item: ApprovalItem): boolean {
    return item.decision === null || (item.decision === "approved" && item.execution_status === "failed")
  }

  // ---- mutators ----
  const handleLaunch = useCallback(async () => {
    if (!businessId) {
      setWebsiteStatus("Business context missing")
      return
    }
    setIsLaunching(true)
    setWebsiteError(null)
    setWebsiteStatus("Website queued")
    sendMessage("Yes, launch my brand and deploy my website! 🚀")
    try {
      const isRetry = websiteStatus === "Website generation failed"
      const res = isRetry
        ? await websitesApi.retry(businessId)
        : await websitesApi.generateAndDeploy(businessId)
      setWebsiteStatus(res?.status === "queued" ? "Website queued" : `Website ${res?.status ?? "status unavailable"}`)
    } catch (err) {
      console.error("Website launch error:", err)
      setWebsiteStatus("Website launch failed")
      setWebsiteError("Could not start website generation. Please try again.")
    } finally {
      setIsLaunching(false)
    }
  }, [businessId, sendMessage, websiteStatus])

  const handleNewConversation = useCallback(() => {
    setDeployedUrl(null)
    setWebsiteStatus("Drafting in Chat")
    setWebsiteError(null)
    setWebsiteAttempts(0)
    setWebsiteLastAttempt(null)
    setReloadKey((k) => k + 1)
  }, [])

  const handleSelectBusiness = useCallback(() => {
    setIsBusinessMenuOpen(false)
    setIsBusinessFormOpen(false)
    setBusinessFormError(null)
    setDeployedUrl(null)
    setWebsiteStatus("Drafting in Chat")
    setWebsiteError(null)
    setWebsiteAttempts(0)
    setWebsiteLastAttempt(null)
    setReloadKey((k) => k + 1)
  }, [])

  const handleCreateBusiness = useCallback(async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const name = newBusinessName.trim()
    if (!name) return
    setIsCreatingBusiness(true)
    setBusinessFormError(null)
    try {
      const business = await businessesApi.create({
        name,
        industry: newBusinessIndustry.trim() || undefined,
      })
      setMyBusinesses((current) => [business, ...current.filter((item) => item.id !== business.id)])
      setIsBusinessMenuOpen(false)
      setIsBusinessFormOpen(false)
      setNewBusinessName("")
      setNewBusinessIndustry("")
      setDeployedUrl(null)
      setWebsiteStatus("Drafting in Chat")
      setWebsiteError(null)
      setWebsiteAttempts(0)
      setWebsiteLastAttempt(null)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setBusinessFormError(err instanceof Error ? err.message : "Could not create this workspace.")
    } finally {
      setIsCreatingBusiness(false)
    }
  }, [newBusinessName, newBusinessIndustry])

  const handleApprove = useCallback(() => {
    // The approval mutate endpoint lives in the backend; here we optimistically
    // refresh the workspace by bumping the reload key so /state re-fetches.
    setReloadKey((k) => k + 1)
  }, [])

  const handleReject = useCallback(() => {
    setReloadKey((k) => k + 1)
  }, [])

  // Brand/context shape still passed to BrandPreviewPane under the old contract.
  const brandContext = state?.latest_brand_kit ? { conversation_stage: "brand", ready_to_generate: true } : { conversation_stage: "greeting", ready_to_generate: false }

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden bg-cream">
      {/* Top Navigation Bar */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-grey-200 bg-white px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-lg font-extrabold tracking-[-0.08em] text-charcoal">
            Cre<span className="text-orange">8</span>ive District
          </Link>
          <span
            role="status"
            aria-label={conversation ? "Abija connected" : "Abija reconnecting"}
            className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-semibold sm:px-2.5 ${
              conversation ? "bg-orange/10 text-orange-hover" : "bg-grey-100 text-grey-500"
            }`}
            title={conversation ? "Connected to Abija" : "Connection lost — reconnecting"}
          >
            <span className={`size-1.5 rounded-full ${conversation ? "bg-orange animate-pulse" : "bg-grey-400"}`} />
            <span className="hidden sm:inline" aria-hidden="true">
              {conversation ? "Abija connected" : "Abija reconnecting"}
            </span>
          </span>

          {/* Business Workspace Switcher */}
          <div className="relative">
            <button
              ref={switcherButtonRef}
              type="button"
              onClick={() => setIsBusinessMenuOpen((v) => !v)}
              className="flex items-center gap-1.5 rounded-lg border border-grey-200 bg-grey-50 px-2.5 py-1 text-xs font-medium text-charcoal hover:bg-grey-100 transition-all cursor-pointer max-w-[200px]"
              title="Switch business workspace"
              aria-haspopup="true"
              aria-expanded={isBusinessMenuOpen}
              aria-controls="business-switcher-menu"
              onKeyDown={(event) => {
                if (event.key === "Escape" && isBusinessMenuOpen) {
                  event.stopPropagation()
                  setIsBusinessMenuOpen(false)
                }
              }}
            >
              <span className="truncate font-semibold">
                {currentBusiness?.name ?? businessName ?? (state?.business?.name ?? "My Workspace")}
              </span>
              <svg className="size-3.5 text-grey-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isBusinessMenuOpen && (
              <>
                <div className="fixed inset-0 z-40" aria-hidden="true" onClick={() => setIsBusinessMenuOpen(false)} />
                <div
                  id="business-switcher-menu"
                  className="absolute left-0 mt-1.5 w-64 rounded-xl border border-grey-200 bg-white p-1.5 shadow-lg z-50 animate-in fade-in zoom-in-95 duration-100"
                  onKeyDown={(event) => {
                    if (event.key === "Escape") {
                      event.stopPropagation()
                      setIsBusinessMenuOpen(false)
                      switcherButtonRef.current?.focus()
                    }
                  }}
                >
                  <div className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-grey-400">
                    My Businesses
                  </div>
                  <div className="max-h-56 overflow-y-auto space-y-0.5">
                    {myBusinesses.length === 0 ? (
                      <div className="px-2.5 py-2 text-xs text-grey-500">No businesses yet</div>
                    ) : (
                      myBusinesses.map((biz) => {
                        const isCurrent = biz.id === businessId
                        return (
                          <button
                            key={biz.id}
                            type="button"
                            onClick={() => handleSelectBusiness()}
                            className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-colors ${
                              isCurrent ? "bg-orange/10 font-bold text-orange" : "text-charcoal hover:bg-grey-50"
                            }`}
                          >
                            <div className="truncate min-w-0 pr-2">
                              <div className="truncate font-medium">{biz.name}</div>
                              <div className="text-[10px] text-grey-400">
                                {biz.industry || "General"} · {biz.credit_balance ?? credits} credits
                              </div>
                            </div>
                            {isCurrent && <span className="text-orange text-xs">✓</span>}
                          </button>
                        )
                      })
                    )}
                  </div>
                  <div className="mt-1 border-t border-grey-100 pt-1">
                    <button
                      type="button"
                      onClick={() => { setIsBusinessFormOpen((v) => !v); setBusinessFormError(null) }}
                      className="flex w-full items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-orange hover:bg-orange/5 transition-colors"
                    >
                      <span>+</span> {isBusinessFormOpen ? "Cancel setup" : "Set up a business"}
                    </button>
                    {isBusinessFormOpen && (
                      <form onSubmit={handleCreateBusiness} className="space-y-2 px-2.5 pb-2 pt-1">
                        <label className="block text-[11px] font-medium text-grey-600">
                          Business name
                          <input
                            autoFocus
                            required
                            maxLength={200}
                            value={newBusinessName}
                            onChange={(e) => setNewBusinessName(e.target.value)}
                            placeholder="e.g. Lagos Threads"
                            className="mt-1 w-full rounded-md border border-grey-200 px-2 py-1.5 text-xs text-charcoal outline-none focus:border-orange"
                          />
                        </label>
                        <label className="block text-[11px] font-medium text-grey-600">
                          Industry <span className="font-normal text-grey-400">(optional)</span>
                          <input
                            maxLength={80}
                            value={newBusinessIndustry}
                            onChange={(e) => setNewBusinessIndustry(e.target.value)}
                            placeholder="e.g. Fashion"
                            className="mt-1 w-full rounded-md border border-grey-200 px-2 py-1.5 text-xs text-charcoal outline-none focus:border-orange"
                          />
                        </label>
                        {businessFormError && (
                          <p role="alert" className="text-[11px] text-red-600">{businessFormError}</p>
                        )}
                        <button
                          type="submit"
                          disabled={isCreatingBusiness || !newBusinessName.trim()}
                          className="w-full rounded-md bg-orange px-2 py-1.5 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {isCreatingBusiness ? "Creating workspace…" : "Create workspace"}
                        </button>
                      </form>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Mobile Tab Toggle */}
        <div className="flex sm:hidden rounded-lg bg-grey-100 p-0.5 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setMobileTab("chat")}
            className={`rounded-md px-3 py-1 transition-all ${
              mobileTab === "chat" ? "bg-white text-charcoal shadow-2xs" : "text-grey-600"
            }`}
          >
            Chat
          </button>
          <button
            type="button"
            onClick={() => setMobileTab("preview")}
            className={`rounded-md px-3 py-1 transition-all ${
              mobileTab === "preview" ? "bg-white text-charcoal shadow-2xs" : "text-grey-600"
            }`}
          >
            Brand Deck
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsTopUpOpen(true)}
            disabled={!businessId}
            className="flex items-center gap-2 rounded-full border border-grey-200 bg-white px-3 py-1 text-xs font-semibold text-charcoal shadow-2xs hover:border-orange hover:bg-orange/5 transition-all cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
            title="Click to view plans & buy credits"
          >
            <span className="text-orange font-bold">⚡ {credits !== null && credits !== undefined ? credits : "—"}</span> credits
            <span className="text-[10px] text-grey-400 font-normal">+ Top up</span>
          </button>
          <button
            type="button"
            onClick={handleNewConversation}
            className="rounded-lg border border-grey-200 bg-white px-3 py-1.5 text-xs font-semibold text-charcoal hover:bg-grey-50 shadow-2xs transition-all"
          >
            + New Brand
          </button>
          {session?.user && (
            <button
              type="button"
              onClick={() => signOut({ callbackUrl: "/sign-in" })}
              className="flex size-8 items-center justify-center rounded-full bg-charcoal text-xs font-bold text-white shadow-2xs hover:ring-2 hover:ring-orange/40"
              title="Sign out"
              aria-label="Sign out"
            >
              {(session.user.name ?? session.user.email ?? "U").charAt(0).toUpperCase()}
            </button>
          )}
        </div>
      </header>

      {loadError && (
        <div role="alert" className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-error/20 bg-error/5 px-4 py-2 text-xs text-charcoal sm:px-6">
          <span>{loadError}</span>
          <button
            type="button"
            onClick={() => { setLoadError(null); setReloadKey((k) => k + 1) }}
            className="rounded-md border border-grey-300 bg-white px-2.5 py-1 text-xs font-semibold text-charcoal hover:bg-grey-50"
          >
            Try again
          </button>
        </div>
      )}

      {/* Pending approvals banner */}
      {pendingApprovals.length > 0 && (
        <div className="flex shrink-0 items-center gap-2 border-b border-orange/20 bg-orange/5 px-4 py-2 text-xs text-charcoal sm:px-6">
          <span className="font-semibold uppercase tracking-wider text-orange">Needs Your OK</span>
          <span className="text-grey-500">{pendingApprovals.length} waiting</span>
        </div>
      )}

      {/* Main Split Screen Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Conversational Chat Stream */}
        <div
          className={`flex-1 h-full min-w-0 ${
            mobileTab === "preview" ? "hidden sm:flex sm:w-7/12" : "flex sm:w-7/12"
          }`}
        >
          <ChatWindow
            messages={conversation ? [{ id: conversation.conversation_id, role: "assistant" as const, content: conversation.greeting ?? "", createdAt: new Date().toISOString(), isStreaming: false }] : []}
            streamingContent=""
            context={brandContext as never}
            isThinking={false}
            isConnected={!!conversation}
            error={null}
            onSendMessage={sendMessage}
            onRestartChat={handleNewConversation}
          />
        </div>

        {/* Right: Live Brand Preview */}
        <div
          className={`h-full sm:w-5/12 sm:flex flex-col ${
            mobileTab === "chat" ? "hidden" : "w-full flex"
          }`}
        >
          <BrandPreviewPane
            context={brandContext as never}
            onLaunch={handleLaunch}
            isLaunching={isLaunching}
            deployedUrl={deployedUrl}
            websiteStatus={websiteStatus}
            websiteError={websiteError}
            websiteAttempts={websiteAttempts}
            websiteLastAttempt={websiteLastAttempt}
            state={state}
            pendingApprovals={pendingApprovals}
            recentApprovals={recentApprovals}
            approvalLabel={approvalLabel}
            isActionable={isActionable}
            onApprove={handleApprove}
            onReject={handleReject}
            onRetry={retry}
          />
        </div>
      </div>

      {/* Approval detail panel (rendered inline under the preview pane on desktop) */}
      {(pendingApprovals.length > 0 || recentApprovals.length > 0) && (
        <div className="flex shrink-0 flex-col border-t border-grey-200 bg-white sm:max-h-64 sm:overflow-y-auto">
          {pendingApprovals.length > 0 && (
            <div className="flex flex-col border-b border-grey-100 px-4 py-2 sm:px-6">
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-grey-400">Needs Your OK</div>
              {pendingApprovals.map((item) => (
                <ApprovalRow
                  key={item.id}
                  item={item}
                  label={approvalLabel(item)}
                  onApprove={() => handleApprove()}
                  onReject={() => handleReject()}
                  onRetry={() => retry(item.id)}
                />
              ))}
            </div>
          )}
          {recentApprovals.length > 0 && (
            <div className="flex flex-col border-t border-grey-100 px-4 py-2 sm:px-6">
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-grey-400">Recent</div>
              {recentApprovals.map((item) => (
                <ApprovalRow
                  key={item.id}
                  item={item}
                  label={approvalLabel(item)}
                  onApprove={() => handleApprove()}
                  onReject={() => handleReject()}
                  onRetry={() => retry(item.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Credit Top-Up Modal */}
      <TopUpModal
        isOpen={isTopUpOpen}
        onClose={() => setIsTopUpOpen(false)}
        businessId={businessId ?? undefined}
        userEmail={session?.user?.email || "founder@cre8ivedistrict.com"}
        currentBalance={credits ?? 0}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tiny inline approval row (keeps the approval state machine in the workspace
// without reaching into a non-existent hook action object)
// ---------------------------------------------------------------------------

interface ApprovalRowProps {
  item: ApprovalItem
  label: string
  onApprove: () => void
  onReject: () => void
  onRetry: () => void
}

function ApprovalRow({ item, label, onApprove, onReject, onRetry }: ApprovalRowProps) {
  return (
    <div className="flex items-start gap-3 border-b border-grey-50 px-3 py-2 last:border-0">
      <div className="min-w-0 flex-1">
        <div className="text-xs font-medium text-charcoal">{item.action_type}</div>
        <div className="text-[11px] text-grey-500">{item.summary}</div>
        <div className="mt-1 text-[11px] font-semibold uppercase tracking-wider text-grey-400">{label}</div>
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        {item.decision === null && (
          <>
            <button type="button" onClick={onApprove} className="rounded-md bg-green-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-green-700">
              Approve
            </button>
            <button type="button" onClick={onReject} className="rounded-md border border-grey-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-charcoal hover:bg-grey-50">
              Reject
            </button>
          </>
        )}
        {(item.decision === "approved" && item.execution_status === "failed") && (
          <button type="button" onClick={onRetry} className="rounded-md bg-orange px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-orange/90">
            Retry
          </button>
        )}
      </div>
    </div>
  )
}
