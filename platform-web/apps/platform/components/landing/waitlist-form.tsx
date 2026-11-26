"use client";

import { useState, type FormEvent } from "react";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function ideaSignupHref(idea: string) {
  const query = new URLSearchParams({ next: "/workspace", idea });
  return `/sign-up?${query.toString()}`;
}

export function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [businessDescription, setBusinessDescription] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success">("idle");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedEmail = email.trim().toLowerCase();
    if (!EMAIL_PATTERN.test(normalizedEmail)) {
      setError("Enter a valid email address so we can record your signup.");
      return;
    }

    setError("");
    setStatus("submitting");
    try {
      const response = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: normalizedEmail,
          source: "platform-home",
          business_description: businessDescription.trim() || undefined,
          company: new FormData(event.currentTarget).get("company"),
        }),
      });

      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as { error?: string } | null;
        setError(payload?.error ?? "We couldn't add you just now. Please try again.");
        setStatus("idle");
        return;
      }

      setStatus("success");
    } catch {
      setError("We couldn't add you just now. Please try again.");
      setStatus("idle");
    }
  }

  if (status === "success") {
    const idea = businessDescription.trim();
    return (
      <div role="status" aria-live="polite" className="rounded-2xl border border-success/25 bg-white p-5 sm:p-6">
        <p className="flex items-center gap-2 text-base font-bold text-charcoal">
          <span aria-hidden="true" className="grid size-6 place-items-center rounded-full bg-success/10 text-sm text-success">✓</span>
          You’re on the list.
        </p>
        <p className="mt-2 text-sm leading-6 text-grey-600">
          Thanks for your interest in Cre8ive District. We’ve recorded your request for early access.
        </p>
        {idea && (
          <a
            href={ideaSignupHref(idea)}
            className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-full bg-orange px-5 text-sm font-bold text-white transition-colors hover:bg-orange-hover"
          >
            Start your workspace with this idea <span aria-hidden="true">→</span>
          </a>
        )}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="rounded-2xl border border-grey-200 bg-white p-4 shadow-[0_18px_55px_rgba(38,31,20,0.06)] sm:p-6">
      <label htmlFor="waitlist-email" className="block text-sm font-semibold">Email address</label>
      <input
        id="waitlist-email"
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
        aria-describedby={error ? "waitlist-error" : "waitlist-hint"}
        className="mt-2 h-12 w-full rounded-lg border border-grey-200 bg-white px-3 text-sm text-charcoal outline-none placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20 aria-[invalid=true]:border-error aria-[invalid=true]:ring-2 aria-[invalid=true]:ring-error/20"
      />
      <label htmlFor="waitlist-business-description" className="mt-4 block text-sm font-semibold">
        What are you building? <span className="font-normal text-grey-600">(optional)</span>
      </label>
      <textarea
        id="waitlist-business-description"
        name="business_description"
        rows={3}
        maxLength={1000}
        value={businessDescription}
        disabled={status === "submitting"}
        onChange={(event) => setBusinessDescription(event.target.value)}
        placeholder="Tell us a little about your business idea..."
        className="mt-2 w-full resize-y rounded-lg border border-grey-200 bg-white px-3 py-2.5 text-sm leading-5 text-charcoal outline-none placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20"
      />
      <input type="text" name="company" tabIndex={-1} autoComplete="off" aria-hidden="true" className="hidden" />
      {error ? (
        <p id="waitlist-error" role="alert" className="mt-3 text-sm text-error">{error}</p>
      ) : (
        <p id="waitlist-hint" className="mt-3 text-xs leading-5 text-grey-600">
          We’ll only use your email for updates about early access.
        </p>
      )}
      <button
        type="submit"
        disabled={status === "submitting"}
        className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-full bg-orange px-5 text-sm font-bold text-white transition hover:bg-orange-hover disabled:cursor-wait disabled:opacity-70 sm:w-auto"
      >
        {status === "submitting" ? "Joining..." : "Join the waitlist"}
        {status !== "submitting" && <span aria-hidden="true">→</span>}
      </button>
    </form>
  );
}
