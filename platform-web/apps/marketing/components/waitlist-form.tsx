"use client";

import { Button } from "@cre8ive/ui";
import { useState, type FormEvent } from "react";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const platformUrl = (process.env.NEXT_PUBLIC_PLATFORM_URL ?? "http://localhost:3001").replace(/\/$/, "");

type Status = "idle" | "submitting" | "success";

export function WaitlistForm({ id, source }: { id: string; source: "hero" | "footer" }) {
  const [email, setEmail] = useState("");
  const [businessDescription, setBusinessDescription] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");

  const emailId = `${id}-email`;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const value = email.trim().toLowerCase();
    if (!EMAIL_PATTERN.test(value)) {
      setError("Enter a valid email address so we can reach you.");
      return;
    }

    setError("");
    setStatus("submitting");

    try {
      const response = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: value,
          source,
          business_description: businessDescription.trim() || undefined,
          company: new FormData(event.currentTarget).get("company"),
        }),
      });

      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as { error?: string } | null;
        setStatus("idle");
        setError(payload?.error ?? "We couldn’t add you just now. Please try again, or email hello@cre8ivedistrict.com.");
        return;
      }

      setStatus("success");
    } catch {
      setStatus("idle");
      setError("We couldn’t add you just now. Please try again, or email hello@cre8ivedistrict.com.");
    }
  }

  if (status === "success") {
    const idea = businessDescription.trim();

    return (
      <div
        role="status"
        aria-live="polite"
        className="w-full rounded-2xl border border-success/25 bg-white p-5 text-left shadow-[0_18px_55px_rgba(38,31,20,0.08)] sm:p-6"
      >
        <p className="flex items-center gap-2 text-base font-bold text-charcoal">
          <span aria-hidden="true" className="grid size-6 place-items-center rounded-full bg-success/10 text-sm text-success">✓</span>
          You’re on the list.
        </p>
        <p className="mt-2 text-sm leading-6 text-grey-600">
          We’ll email <span className="font-semibold text-charcoal">{email.trim()}</span> when early access opens.
        </p>
        {idea && (
          <a
            href={`${platformUrl}/sign-in?idea=${encodeURIComponent(idea)}`}
            className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-full bg-orange px-5 text-sm font-bold text-charcoal transition-colors hover:bg-orange-hover"
          >
            Start your workspace with this idea <span aria-hidden="true">→</span>
          </a>
        )}
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="w-full rounded-2xl border border-charcoal/15 bg-white p-3 text-left shadow-[0_18px_55px_rgba(38,31,20,0.08)] sm:p-4"
    >
      <div className="flex flex-col gap-2 sm:flex-row">
        <div className="min-w-0 flex-1">
          <label htmlFor={emailId} className="sr-only">Email address</label>
          <input
            id={emailId}
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            required
            maxLength={254}
            value={email}
            disabled={status === "submitting"}
            onChange={(event) => {
              setEmail(event.target.value);
              if (error) setError("");
            }}
            placeholder="you@business.com"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? `${id}-error` : `${id}-hint`}
            className="h-11 w-full rounded-lg border border-grey-200 bg-white px-3 text-sm text-charcoal outline-none placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20 aria-[invalid=true]:border-error aria-[invalid=true]:ring-2 aria-[invalid=true]:ring-error/20"
          />
        </div>
        <Button
          type="submit"
          loading={status === "submitting"}
          className="h-11 shrink-0 rounded-lg px-5"
        >
          Join waitlist <span aria-hidden="true">→</span>
        </Button>
      </div>

      <div className="mt-3 px-1">
        <label htmlFor={`${id}-business-description`} className="mb-1.5 block text-xs font-semibold text-charcoal">
          Tell us about your business <span className="font-normal text-grey-600">(optional)</span>
        </label>
        <textarea
          id={`${id}-business-description`}
          name="business_description"
          rows={2}
          maxLength={1000}
          value={businessDescription}
          disabled={status === "submitting"}
          onChange={(event) => setBusinessDescription(event.target.value)}
          placeholder="What do you sell, or what are you planning to build?"
          className="w-full resize-y rounded-lg border border-grey-200 bg-white px-3 py-2 text-sm leading-5 text-charcoal outline-none placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20"
        />
      </div>

      {/* Honeypot for bots; hidden from people and assistive technology. */}
      <input
        type="text"
        name="company"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        className="hidden"
      />

      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-2.5 px-1 text-sm text-error">{error}</p>
      ) : (
        <p id={`${id}-hint`} className="mt-2.5 px-1 text-xs leading-5 text-grey-600">
          Early access and launch updates only. Unsubscribe anytime.
        </p>
      )}
    </form>
  );
}
