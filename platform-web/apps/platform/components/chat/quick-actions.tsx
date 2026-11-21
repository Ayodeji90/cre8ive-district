"use client";

import type { ExtractedBrandContext } from "../../hooks/use-abija-chat";

interface QuickActionsProps {
  context: ExtractedBrandContext;
  onSelect: (actionText: string) => void;
  disabled?: boolean;
}

export function QuickActions({ context, onSelect, disabled = false }: QuickActionsProps) {
  const stage = context.conversation_stage ?? "greeting";

  let options: string[] = [];

  if (context.ready_to_generate || stage === "summary_confirm") {
    options = [
      "Yes, create my brand and website now! 🚀",
      "I love it, let's launch! ✨",
      "Can we adjust the colors first?",
    ];
  } else if (stage === "style_preferences") {
    options = [
      "Modern, clean and luxury 💎",
      "Bold, vibrant and Afro-inspired 🔥",
      "Warm, friendly and accessible 🌿",
      "High-energy and digital ⚡",
    ];
  } else if (stage === "target_audience" || stage === "industry_refine") {
    options = [
      "Young urban professionals in Lagos & Abuja 🏙️",
      "African diaspora looking for authentic products 🌍",
      "Everyday shoppers looking for quality & fast WhatsApp support 📱",
      "Corporate clients and B2B businesses 💼",
    ];
  } else {
    // greeting or business_description
    options = [
      "Afrocentric ready-to-wear fashion label in Lagos",
      "Tech-enabled logistics & delivery service for local vendors",
      "Artisanal specialty coffee & café in Nairobi",
      "Organic skincare line formulated with African botanicals",
    ];
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5 py-1.5">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(opt)}
          className="inline-flex items-center rounded-full border border-grey-200 bg-white px-3 py-1 text-xs font-medium text-charcoal shadow-2xs hover:border-orange hover:bg-orange/5 hover:text-orange-hover active:scale-95 disabled:pointer-events-none disabled:opacity-50 transition-all"
        >
          {opt}
        </button>
      ))}
    </div>
  );
}
