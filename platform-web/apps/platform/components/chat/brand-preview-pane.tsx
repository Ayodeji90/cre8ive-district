"use client";

import type { ExtractedBrandContext } from "../../hooks/use-abija-chat";

interface BrandPreviewPaneProps {
  context: ExtractedBrandContext;
  onLaunch?: () => void;
  isLaunching?: boolean;
  deployedUrl?: string | null;
  websiteStatus?: string;
  websiteError?: string | null;
  websiteAttempts?: number;
  websiteLastAttempt?: string | null;
}

export function BrandPreviewPane({
  context,
  onLaunch,
  isLaunching = false,
  deployedUrl = null,
  websiteStatus,
  websiteError,
  websiteAttempts = 0,
  websiteLastAttempt = null,
}: BrandPreviewPaneProps) {
  const brandName = context.business_name || "Your Brand Name";
  const industry = context.industry || "African Commerce";
  const mood = context.mood || "Warm, Confident & Distinctive";
  const isReady = Boolean(context.ready_to_generate);

  // Dynamic palette extraction or fallbacks
  const rawPalette = (context.palette as { primary?: string; secondary?: string; accent?: string; background?: string } | undefined) || {};
  const primaryColor = rawPalette.primary || "#F36B35";
  const secondaryColor = rawPalette.secondary || "#2D2D2D";
  const accentColor = rawPalette.accent || "#F4B942";
  const bgColor = rawPalette.background || "#FAF8F5";

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-white border-l border-grey-200 p-6 lg:p-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-grey-100 pb-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-orange">
            Live Brand Deck
          </span>
          <h2 className="text-xl font-bold tracking-tight text-charcoal">
            {context.business_name ? context.business_name : "Shaping your identity"}
          </h2>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
            isReady
              ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
              : "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
          }`}
        >
          <span
            className={`size-1.5 rounded-full ${
              isReady ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
            }`}
          />
          {isReady ? "Ready to Launch" : "Drafting in Chat"}
        </span>
      </div>

      {/* Brand Card Preview */}
      <div className="mt-6 rounded-2xl border border-grey-200 bg-linear-to-br from-[#FAF8F5] to-white p-6 shadow-xs">
        <div className="flex items-start justify-between">
          <div
            className="size-14 rounded-xl flex items-center justify-center text-white text-2xl font-black shadow-md"
            style={{ backgroundColor: primaryColor }}
          >
            {brandName.charAt(0).toUpperCase()}
          </div>
          <span className="text-xs font-medium text-grey-500 rounded-md bg-white px-2 py-1 border border-grey-150">
            {industry}
          </span>
        </div>

        <h3 className="mt-4 text-2xl font-extrabold tracking-tight text-charcoal">
          {brandName}
        </h3>
        <p className="mt-1 text-xs text-grey-600 line-clamp-2">
          {context.description || "Every brand begins with an idea. Abija is listening to your conversation to craft this identity."}
        </p>

        {/* Color Palette Swatches */}
        <div className="mt-5 pt-4 border-t border-grey-200/60">
          <p className="text-[11px] font-bold uppercase tracking-wider text-grey-600 mb-2">
            Dynamic Color Palette
          </p>
          <div className="flex items-center gap-2">
            <div
              className="group relative flex-1 h-9 rounded-lg shadow-inner transition-transform hover:scale-105 flex items-center justify-center text-[10px] text-white font-mono opacity-90"
              style={{ backgroundColor: primaryColor }}
            >
              {primaryColor}
            </div>
            <div
              className="group relative flex-1 h-9 rounded-lg shadow-inner transition-transform hover:scale-105 flex items-center justify-center text-[10px] text-white font-mono opacity-90"
              style={{ backgroundColor: secondaryColor }}
            >
              {secondaryColor}
            </div>
            <div
              className="group relative flex-1 h-9 rounded-lg shadow-inner transition-transform hover:scale-105 flex items-center justify-center text-[10px] text-charcoal font-mono opacity-90"
              style={{ backgroundColor: accentColor }}
            >
              {accentColor}
            </div>
            <div
              className="group relative flex-1 h-9 rounded-lg border border-grey-200 shadow-inner transition-transform hover:scale-105 flex items-center justify-center text-[10px] text-grey-600 font-mono"
              style={{ backgroundColor: bgColor }}
            >
              {bgColor}
            </div>
          </div>
        </div>

        {/* Typography Specs */}
        <div className="mt-5 pt-4 border-t border-grey-200/60 flex items-center justify-between text-xs">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-grey-600 block">
              Typography
            </span>
            <span className="font-semibold text-charcoal">Plus Jakarta Sans</span>
          </div>
          <div className="text-right">
            <span className="text-[11px] font-bold uppercase tracking-wider text-grey-600 block">
              Vibe
            </span>
            <span className="font-semibold text-orange-hover">{mood}</span>
          </div>
        </div>
      </div>

      {/* Website & Autonomous Run Status */}
      <div className="mt-6 space-y-3">
        <div className="flex items-center gap-3 rounded-xl border border-grey-200 bg-white p-3.5 shadow-2xs">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 text-lg">
            🌐
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold text-charcoal">
              {deployedUrl
                ? "Website Deployed & Live ✓"
                : isLaunching
                ? "Generating Website..."
                : websiteStatus || "Static Website Layout"}
            </p>
            <p className="text-[11px] text-grey-500">
              {deployedUrl ? (
                <a
                  href={deployedUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-orange hover:underline font-semibold"
                >
                  {deployedUrl} →
                </a>
              ) : (
                "Brand-matched pages with a responsive static layout"
              )}
            </p>
            {websiteError && <p role="alert" className="text-[11px] text-red-600">{websiteError}</p>}
            {websiteAttempts > 0 && !deployedUrl && (
              <p className="text-[10px] text-grey-500" title={websiteLastAttempt || undefined}>
                Attempt {websiteAttempts}{websiteLastAttempt ? ` · ${new Date(websiteLastAttempt).toLocaleString()}` : ""}
              </p>
            )}
          </div>
          <span className={`text-xs font-semibold ${deployedUrl ? "text-emerald-600" : "text-grey-500"}`}>
            {deployedUrl ? "Live" : websiteStatus?.toLowerCase().includes("queued") ? "Queued" : "Not live"}
          </span>
        </div>

        <div className="flex items-center gap-3 rounded-xl border border-grey-200 bg-white p-3.5 shadow-2xs">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-orange/10 text-orange text-lg">
            ⚡
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold text-charcoal">Autonomous Run Engine</p>
            <p className="text-[11px] text-grey-500">Outreach, competitor scan & marketing loop</p>
          </div>
          <span className="text-xs font-semibold text-orange">Standby</span>
        </div>
      </div>

      {/* Launch Action */}
      <div className="mt-auto pt-6">
        <button
          type="button"
          disabled={!isReady || isLaunching}
          onClick={onLaunch}
          className={`w-full h-12 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-sm transition-all ${
            isReady
              ? "bg-orange text-white hover:bg-orange-hover active:scale-[0.98] cursor-pointer"
              : "bg-grey-150 text-grey-600 cursor-not-allowed"
          }`}
        >
          {isLaunching ? (
            <>
              <span className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
              <span>Generating Brand Package...</span>
            </>
          ) : isReady ? (
            <>
              <span>{websiteStatus === "Website generation failed" ? "Retry Website Generation" : "Launch Brand & Deploy Website"}</span>
              <span aria-hidden="true">🚀</span>
            </>
          ) : (
            <span>Tell Abija more to unlock launch</span>
          )}
        </button>
        <p className="mt-2 text-center text-[11px] text-grey-600">
          Generated by Abija • Optional designer review
        </p>
      </div>
    </div>
  );
}
