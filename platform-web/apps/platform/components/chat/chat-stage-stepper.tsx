"use client";

import type { ExtractedBrandContext } from "../../hooks/use-abija-chat";

interface ChatStageStepperProps {
  context: ExtractedBrandContext;
}

const STAGES = [
  { id: "business_description", label: "1. Idea", desc: "Concept" },
  { id: "target_audience", label: "2. Audience", desc: "Customers" },
  { id: "style_preferences", label: "3. Brand Vibe", desc: "Aesthetic" },
  { id: "launch", label: "4. Launch", desc: "Brand & Web" },
];

function getStageIndex(stageName?: string, readyToGenerate?: boolean): number {
  if (readyToGenerate || stageName === "complete" || stageName === "summary_confirm") {
    return 3;
  }
  switch (stageName) {
    case "greeting":
      return 0;
    case "business_description":
      return 0;
    case "industry_refine":
    case "target_audience":
      return 1;
    case "style_preferences":
      return 2;
    default:
      return 0;
  }
}

export function ChatStageStepper({ context }: ChatStageStepperProps) {
  const currentStageIndex = getStageIndex(context.conversation_stage, context.ready_to_generate);

  return (
    <div className="w-full border-b border-grey-200 bg-white/70 backdrop-blur-sm px-4 py-3 sm:px-6">
      {/* Step Indicators */}
      <div className="flex items-center justify-between gap-2 max-w-2xl mx-auto">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStageIndex;
          const isCurrent = idx === currentStageIndex;

          return (
            <div key={stage.id} className="flex items-center gap-2 flex-1">
              <div className="flex items-center gap-2 min-w-0">
                <div
                  className={`flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                    isDone
                      ? "bg-emerald-600 text-white"
                      : isCurrent
                      ? "bg-orange text-white ring-2 ring-orange/30"
                      : "bg-grey-100 text-grey-500"
                  }`}
                >
                  {isDone ? "✓" : idx + 1}
                </div>
                <div className="hidden sm:block truncate">
                  <p className={`text-xs font-semibold leading-none ${isCurrent ? "text-charcoal" : "text-grey-500"}`}>
                    {stage.label}
                  </p>
                </div>
              </div>
              {idx < STAGES.length - 1 && (
                <div
                  className={`h-0.5 flex-1 transition-colors ${
                    idx < currentStageIndex ? "bg-emerald-500" : "bg-grey-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Extracted Facts Pill Bar */}
      {(context.business_name || context.industry || context.target_audience || context.mood) && (
        <div className="mt-2.5 flex flex-wrap items-center gap-1.5 pt-2 border-t border-grey-100 max-w-2xl mx-auto">
          <span className="text-[11px] font-bold uppercase tracking-wider text-grey-600 mr-1">
            Abija noted:
          </span>
          {context.business_name && (
            <span className="inline-flex items-center rounded-full bg-orange/10 px-2 py-0.5 text-xs font-medium text-orange-hover">
              🏷️ {context.business_name}
            </span>
          )}
          {context.industry && (
            <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
              🏢 {context.industry}
            </span>
          )}
          {context.target_audience && (
            <span className="inline-flex items-center rounded-full bg-purple-50 px-2 py-0.5 text-xs font-medium text-purple-700">
              👥 {context.target_audience}
            </span>
          )}
          {context.mood && (
            <span className="inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800">
              ✨ {context.mood}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
