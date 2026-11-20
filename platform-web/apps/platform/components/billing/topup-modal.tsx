"use client";

import { useState } from "react";
import { billingApi } from "@cre8ive/api-client";

interface TopUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  businessId?: string;
  userEmail?: string;
  currentBalance: number;
}

const CREDIT_PACKS = [
  {
    id: "credits_50" as const,
    credits: 50,
    price: "₦5,000",
    label: "Starter Pack",
    desc: "10 social posts or 5 deep competitor scans",
    popular: false,
  },
  {
    id: "credits_200" as const,
    credits: 200,
    price: "₦18,000",
    label: "Growth Pack",
    desc: "Save 10% — Continuous runs & weekly outreach",
    popular: true,
  },
  {
    id: "credits_500" as const,
    credits: 500,
    price: "₦40,000",
    label: "Pro Scale Pack",
    desc: "Save 20% — Full autonomous marketing cycle",
    popular: false,
  },
];

export function TopUpModal({
  isOpen,
  onClose,
  businessId,
  userEmail,
  currentBalance,
}: TopUpModalProps) {
  const [selectedPack, setSelectedPack] = useState<"credits_50" | "credits_200" | "credits_500">("credits_200");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCheckout = async () => {
    if (!businessId || !userEmail) {
      setError("Please ensure you are connected to a business workspace.");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const res = await billingApi.topupCredits(businessId, selectedPack, userEmail);
      if (res.authorization_url) {
        window.location.href = res.authorization_url;
      } else {
        setError("Could not retrieve Paystack payment link. Please try again.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to initiate payment";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl sm:p-8">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-grey-400 hover:bg-grey-100 hover:text-charcoal transition-colors"
          aria-label="Close"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="text-center sm:text-left">
          <span className="text-[11px] font-extrabold uppercase tracking-widest text-orange">
            Fuel Abija&apos;s Autonomous Engine
          </span>
          <h2 className="mt-1 text-2xl font-black tracking-tight text-charcoal">
            Top Up Credits
          </h2>
          <p className="mt-1 text-xs text-grey-600">
            Current balance: <span className="font-bold text-orange">{currentBalance} credits</span>.
            Credits power autonomous tasks like competitor scans, outreach, and social campaigns.
          </p>
        </div>

        {/* Packs Grid */}
        <div className="mt-6 space-y-3">
          {CREDIT_PACKS.map((pack) => {
            const isSelected = selectedPack === pack.id;
            return (
              <div
                key={pack.id}
                onClick={() => setSelectedPack(pack.id)}
                className={`relative flex cursor-pointer items-center justify-between rounded-xl border p-4 transition-all ${
                  isSelected
                    ? "border-orange bg-orange/5 ring-2 ring-orange/20 shadow-xs"
                    : "border-grey-200 bg-white hover:border-grey-300"
                }`}
              >
                {pack.popular && (
                  <span className="absolute -top-2.5 right-4 rounded-full bg-orange px-2 py-0.5 text-[10px] font-bold text-white shadow-xs">
                    MOST POPULAR
                  </span>
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-charcoal">{pack.label}</span>
                    <span className="rounded-md bg-grey-150 px-1.5 py-0.5 text-[11px] font-bold text-orange-hover">
                      +{pack.credits} Credits
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-grey-500">{pack.desc}</p>
                </div>
                <div className="text-right">
                  <span className="text-base font-black text-charcoal">{pack.price}</span>
                  <span className="block text-[10px] text-grey-600">Paystack secure</span>
                </div>
              </div>
            );
          })}
        </div>

        {error && (
          <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-2.5 text-center text-xs text-red-600">
            {error}
          </div>
        )}

        {/* Paystack CTA */}
        <div className="mt-6">
          <button
            type="button"
            disabled={isLoading}
            onClick={handleCheckout}
            className="w-full h-12 rounded-xl bg-orange text-white font-bold text-sm flex items-center justify-center gap-2 hover:bg-orange-hover active:scale-[0.99] disabled:opacity-50 transition-all shadow-sm"
          >
            {isLoading ? (
              <>
                <span className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
                <span>Redirecting to Paystack...</span>
              </>
            ) : (
              <>
                <span>Pay with Paystack</span>
                <span aria-hidden="true">🔒</span>
              </>
            )}
          </button>
          <div className="mt-2.5 flex items-center justify-center gap-2 text-[11px] text-grey-600">
            <span>Debit Cards • Bank Transfer • USSD • Apple Pay</span>
          </div>
        </div>
      </div>
    </div>
  );
}
