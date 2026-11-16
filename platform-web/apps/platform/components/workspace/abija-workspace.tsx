"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { signOut, useSession } from "next-auth/react";
import { billingApi, businessesApi, websitesApi, type Business } from "@cre8ive/api-client";
import { useAbijaChat } from "../../hooks/use-abija-chat";
import { ChatWindow } from "../chat/chat-window";
import { BrandPreviewPane } from "../chat/brand-preview-pane";
import { TopUpModal } from "../billing/topup-modal";

interface AbijaWorkspaceProps {
  initialIdea?: string;
}

export function AbijaWorkspace({ initialIdea }: AbijaWorkspaceProps) {
  const { data: session, status: sessionStatus } = useSession();
  const [mobileTab, setMobileTab] = useState<"chat" | "preview">("chat");
  const [isLaunching, setIsLaunching] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [isTopUpOpen, setIsTopUpOpen] = useState(false);
  const [credits, setCredits] = useState<number | null>(null);
  const [deployedUrl, setDeployedUrl] = useState<string | null>(null);
  const [websiteStatus, setWebsiteStatus] = useState<string>("Drafting in Chat");
  const [websiteError, setWebsiteError] = useState<string | null>(null);
  const [websiteAttempts, setWebsiteAttempts] = useState(0);
  const [websiteLastAttempt, setWebsiteLastAttempt] = useState<string | null>(null);

  // Business workspace selection
  const [myBusinesses, setMyBusinesses] = useState<Business[]>([]);
  const [isBusinessMenuOpen, setIsBusinessMenuOpen] = useState(false);
  const [isBusinessFormOpen, setIsBusinessFormOpen] = useState(false);
  const [newBusinessName, setNewBusinessName] = useState("");
  const [newBusinessIndustry, setNewBusinessIndustry] = useState("");
  const [businessFormError, setBusinessFormError] = useState<string | null>(null);
  const [isCreatingBusiness, setIsCreatingBusiness] = useState(false);

  const {
    messages,
    streamingContent,
    context,
    isThinking,
    isConnected,
    error,
    startConversation,
    sendMessage,
  } = useAbijaChat(undefined, session?.accessToken);

  const businessId = (context.business_id as string) || null;

  const refreshBusinesses = () => {
    if (sessionStatus === "authenticated" && session?.user) {
      businessesApi
        .list()
        .then((list) => {
          if (Array.isArray(list)) {
            setMyBusinesses(list);
          }
        })
        .catch(() => {});
    }
  };

  useEffect(() => {
    refreshBusinesses();
  }, [session, sessionStatus, businessId]);

  // Initialize conversation on mount if not started
  useEffect(() => {
    if (sessionStatus === "authenticated" && !hasStarted) {
      setHasStarted(true);
      startConversation(initialIdea);
    }
  }, [hasStarted, initialIdea, sessionStatus, startConversation]);

  // Fetch live credit balance whenever businessId changes or on connect
  useEffect(() => {
    if (!businessId) return;
    billingApi
      .credits(businessId)
      .then((res) => {
        if (res?.balance !== undefined) {
          setCredits(res.balance);
        }
      })
      .catch(() => {});

    // Recover existing website deployment state if available
    websitesApi
      .getStatus(businessId)
      .then((res) => {
        setWebsiteAttempts(res.attempt_count || 0);
        setWebsiteLastAttempt(res.last_attempt_at);
        if (res?.deployment_url && res.status === "deployed") {
          setDeployedUrl(res.deployment_url);
          setWebsiteStatus("Website Deployed & Live ✓");
        } else if (res?.status) {
          setWebsiteStatus(res.status === "failed" ? "Website generation failed" : `Website ${res.status}`);
          setWebsiteError(res.last_error);
        }
      })
      .catch(() => {});
  }, [businessId]);

  const handleLaunch = async () => {
    if (!businessId) {
      setWebsiteStatus("Business context missing");
      return;
    }
    setIsLaunching(true);
    setWebsiteError(null);
    setWebsiteStatus("Website queued");
    sendMessage("Yes, launch my brand and deploy my website! 🚀");

    try {
      const isRetry = websiteStatus === "Website generation failed";
      const res = isRetry
        ? await websitesApi.retry(businessId)
        : await websitesApi.generateAndDeploy(businessId);
      setWebsiteStatus(res?.status === "queued" ? "Website queued" : `Website ${res?.status ?? "status unavailable"}`);
    } catch (err) {
      console.error("Website launch error:", err);
      setWebsiteStatus("Website launch failed");
      setWebsiteError("Could not start website generation. Please try again.");
    } finally {
      setIsLaunching(false);
    }
  };

  useEffect(() => {
    if (!businessId || !["queued", "generating"].some((state) => websiteStatus.toLowerCase().includes(state))) return;
    const timer = window.setInterval(() => {
      websitesApi.getStatus(businessId).then((res) => {
        setWebsiteAttempts(res.attempt_count || 0);
        setWebsiteLastAttempt(res.last_attempt_at);
        if (res?.status === "deployed" && res.deployment_url) {
          setDeployedUrl(res.deployment_url);
          setWebsiteStatus("Website Deployed & Live ✓");
          setWebsiteError(null);
        } else if (res?.status === "failed") {
          setWebsiteStatus("Website generation failed");
          setWebsiteError(res.last_error || "Website generation failed. Retry the job or contact support.");
        } else if (res?.last_error) {
          setWebsiteError(res.last_error);
        }
      }).catch(() => {});
    }, 2500);
    return () => window.clearInterval(timer);
  }, [businessId, websiteStatus]);

  const handleNewConversation = () => {
    setDeployedUrl(null);
    setWebsiteStatus("Drafting in Chat");
    setWebsiteError(null);
    setWebsiteAttempts(0);
    setWebsiteLastAttempt(null);
    startConversation(undefined, businessId ?? undefined);
  };

  const handleSelectBusiness = (biz: Business) => {
    setIsBusinessMenuOpen(false);
    setIsBusinessFormOpen(false);
    setBusinessFormError(null);
    setDeployedUrl(null);
    setWebsiteStatus("Drafting in Chat");
    setWebsiteError(null);
    setWebsiteAttempts(0);
    setWebsiteLastAttempt(null);
    startConversation(undefined, biz.id);
  };

  const handleCreateBusiness = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const name = newBusinessName.trim();
    if (!name) return;

    setIsCreatingBusiness(true);
    setBusinessFormError(null);
    try {
      const business = await businessesApi.create({
        name,
        industry: newBusinessIndustry.trim() || undefined,
      });
      setMyBusinesses((current) => [business, ...current.filter((item) => item.id !== business.id)]);
      setIsBusinessMenuOpen(false);
      setIsBusinessFormOpen(false);
      setNewBusinessName("");
      setNewBusinessIndustry("");
      setDeployedUrl(null);
      setWebsiteStatus("Drafting in Chat");
      setWebsiteError(null);
      setWebsiteAttempts(0);
      setWebsiteLastAttempt(null);
      startConversation(undefined, business.id);
    } catch (err) {
      setBusinessFormError(err instanceof Error ? err.message : "Could not create this workspace.");
    } finally {
      setIsCreatingBusiness(false);
    }
  };

  const currentBusiness = myBusinesses.find((b) => b.id === businessId);

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden bg-cream">
      {/* Top Navigation Bar */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-grey-200 bg-white px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-lg font-extrabold tracking-[-0.08em] text-charcoal">
            Cre<span className="text-orange">8</span>ive District
          </Link>
          <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-orange/10 px-2.5 py-0.5 text-xs font-semibold text-orange-hover">
            <span className="size-1.5 rounded-full bg-orange animate-pulse" />
            Abija Agent Active
          </span>

          {/* Business Workspace Switcher */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsBusinessMenuOpen(!isBusinessMenuOpen)}
              className="flex items-center gap-1.5 rounded-lg border border-grey-200 bg-grey-50 px-2.5 py-1 text-xs font-medium text-charcoal hover:bg-grey-100 transition-all cursor-pointer max-w-[200px]"
              title="Switch business workspace"
            >
              <span className="truncate font-semibold">
                {currentBusiness?.name || (context.business_name as string) || "My Workspace"}
              </span>
              <svg className="size-3.5 text-grey-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isBusinessMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setIsBusinessMenuOpen(false)}
                />
                <div className="absolute left-0 mt-1.5 w-64 rounded-xl border border-grey-200 bg-white p-1.5 shadow-lg z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-grey-400">
                    My Businesses
                  </div>
                  <div className="max-h-56 overflow-y-auto space-y-0.5">
                    {myBusinesses.length === 0 ? (
                      <div className="px-2.5 py-2 text-xs text-grey-500">No businesses yet</div>
                    ) : (
                      myBusinesses.map((biz) => {
                        const isCurrent = biz.id === businessId;
                        return (
                          <button
                            key={biz.id}
                            type="button"
                            onClick={() => handleSelectBusiness(biz)}
                            className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-colors ${
                              isCurrent
                                ? "bg-orange/10 font-bold text-orange"
                                : "text-charcoal hover:bg-grey-50"
                            }`}
                          >
                            <div className="truncate min-w-0 pr-2">
                              <div className="truncate font-medium">{biz.name}</div>
                              <div className="text-[10px] text-grey-400">
                                {biz.industry || "General"} · {biz.credit_balance} credits
                              </div>
                            </div>
                            {isCurrent && <span className="text-orange text-xs">✓</span>}
                          </button>
                        );
                      })
                    )}
                  </div>
                  <div className="mt-1 border-t border-grey-100 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setIsBusinessFormOpen((open) => !open);
                        setBusinessFormError(null);
                      }}
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
                            onChange={(event) => setNewBusinessName(event.target.value)}
                            placeholder="e.g. Lagos Threads"
                            className="mt-1 w-full rounded-md border border-grey-200 px-2 py-1.5 text-xs text-charcoal outline-none focus:border-orange"
                          />
                        </label>
                        <label className="block text-[11px] font-medium text-grey-600">
                          Industry <span className="font-normal text-grey-400">(optional)</span>
                          <input
                            maxLength={80}
                            value={newBusinessIndustry}
                            onChange={(event) => setNewBusinessIndustry(event.target.value)}
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
            <span className="text-orange font-bold">⚡ {credits !== null ? credits : "—"}</span> credits
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

      {/* Main Split Screen Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Conversational Chat Stream */}
        <div
          className={`flex-1 h-full min-w-0 ${
            mobileTab === "preview" ? "hidden sm:flex sm:w-7/12" : "flex sm:w-7/12"
          }`}
        >
          <ChatWindow
            messages={messages}
            streamingContent={streamingContent}
            context={context}
            isThinking={isThinking}
            isConnected={isConnected}
            error={error}
            onSendMessage={sendMessage}
            onRestartChat={handleNewConversation}
          />
        </div>

        {/* Right: Foundable-Style Live Brand Preview */}
        <div
          className={`h-full sm:w-5/12 sm:flex flex-col ${
            mobileTab === "chat" ? "hidden" : "w-full flex"
          }`}
        >
          <BrandPreviewPane
            context={context}
            onLaunch={handleLaunch}
            isLaunching={isLaunching}
            deployedUrl={deployedUrl}
            websiteStatus={websiteStatus}
            websiteError={websiteError}
            websiteAttempts={websiteAttempts}
            websiteLastAttempt={websiteLastAttempt}
          />
        </div>
      </div>

      {/* Credit Top-Up Modal */}
      <TopUpModal
        isOpen={isTopUpOpen}
        onClose={() => setIsTopUpOpen(false)}
        businessId={businessId ?? undefined}
        userEmail={session?.user?.email || "founder@cre8ivedistrict.com"}
        currentBalance={credits ?? 0}
      />
    </div>
  );
}
