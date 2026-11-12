"use client";

import { Button, toast } from "@cre8ive/ui";
import { signIn } from "next-auth/react";
import Link from "next/link";
import { useState, type FormEvent } from "react";

export function AuthForm({ mode }: { mode: "sign-in" | "sign-up" }) {
  const [email, setEmail] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [sent, setSent] = useState(false);
  const isSignUp = mode === "sign-up";

  async function handleEmailSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSending(true);
    try {
      const result = await signIn("resend", { email, redirect: false, callbackUrl: "/welcome" });
      if (result?.error) throw new Error(result.error);
      setSent(true);
      toast.success("Your sign-in link is on its way.");
    } catch {
      toast.error("We couldn’t send your link. Check the email address and try again.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="w-full max-w-md rounded-2xl border border-grey-200 bg-white p-6 shadow-[0_18px_55px_rgba(38,31,20,0.08)] sm:p-9">
      <div className="text-center">
        <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">Your launch workspace</p>
        <h1 className="mt-3 text-3xl font-extrabold tracking-[-0.06em] text-charcoal">{isSignUp ? "Create your account" : "Log in to your workspace"}</h1>
        <p className="mt-2 text-sm leading-6 text-grey-600">{isSignUp ? "Start turning your business idea into a brand." : "Pick up where you left off with Abija."}</p>
      </div>

      <Button type="button" variant="secondary" className="mt-7 h-12 w-full" onClick={() => void signIn("google", { callbackUrl: "/" })}>
        <GoogleMark /> Continue with Google
      </Button>

      <div className="my-6 flex items-center gap-3 text-xs text-grey-400"><span className="h-px flex-1 bg-grey-200" />or continue with email<span className="h-px flex-1 bg-grey-200" /></div>

      <form onSubmit={handleEmailSubmit} className="grid gap-3">
        <label htmlFor="email" className="text-sm font-semibold text-charcoal">Email address</label>
        <input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" className="h-11 rounded-md border border-grey-200 bg-white px-3 text-sm text-charcoal outline-none placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20" />
        <Button type="submit" loading={isSending} className="mt-1 h-12 w-full">{sent ? "Send another link" : "Send magic link"} <span aria-hidden="true">→</span></Button>
        {sent && <p role="status" className="text-center text-sm text-success">Check your inbox for a secure sign-in link.</p>}
      </form>
      <p className="mt-6 text-center text-sm text-grey-600">
        {isSignUp ? "Already have an account? " : "Don’t have an account? "}
        <Link href={isSignUp ? "/sign-in" : "/sign-up"} className="font-bold text-orange-hover hover:underline">{isSignUp ? "Log in" : "Sign up"}</Link>
      </p>
    </div>
  );
}

function GoogleMark() {
  return <svg aria-hidden="true" viewBox="0 0 20 20" className="size-5"><path fill="#4285F4" d="M19.6 10.23c0-.68-.06-1.36-.18-2.02H10v3.83h5.38a4.6 4.6 0 0 1-2 3.02v2.48h3.24c1.9-1.75 2.98-4.33 2.98-7.31Z"/><path fill="#34A853" d="M10 20c2.7 0 4.96-.9 6.62-2.46l-3.24-2.48c-.9.6-2.04.96-3.38.96-2.6 0-4.8-1.76-5.6-4.12H1.05v2.56A10 10 0 0 0 10 20Z"/><path fill="#FBBC05" d="M4.4 11.9a6 6 0 0 1 0-3.8V5.54H1.05a10 10 0 0 0 0 8.92L4.4 11.9Z"/><path fill="#EA4335" d="M10 3.98c1.47 0 2.8.5 3.84 1.52l2.88-2.88A9.6 9.6 0 0 0 10 0a10 10 0 0 0-8.95 5.54L4.4 8.1C5.2 5.74 7.4 3.98 10 3.98Z"/></svg>;
}
