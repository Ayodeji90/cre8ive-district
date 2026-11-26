"use client";

import Link from "next/link";
import { useState } from "react";
import { AbijaAvatar } from "../chat/abija-avatar";

type LandingTab = "overview" | "abija";

function authHref(mode: "sign-in" | "sign-up", idea: string) {
  const query = new URLSearchParams({ next: "/workspace" });
  if (idea) query.set("idea", idea);
  return `/${mode}?${query.toString()}`;
}

export function PlatformLanding({ initialIdea = "" }: { initialIdea?: string }) {
  const [idea, setIdea] = useState(initialIdea.trim().slice(0, 2000));
  const [activeTab, setActiveTab] = useState<LandingTab>(initialIdea.trim() ? "abija" : "overview");
  const cleanIdea = idea.trim();
  const signUpHref = authHref("sign-up", cleanIdea);
  const signInHref = authHref("sign-in", cleanIdea);

  return (
    <main className="min-h-screen bg-cream text-charcoal">
      <header className="border-b border-grey-200/80 bg-cream/90">
        <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link href="/" className="text-lg font-extrabold tracking-[-0.07em]" aria-label="Cre8ive District home">
            Cre<span className="text-orange">8</span>ive District
          </Link>
          <nav aria-label="Main navigation" className="flex items-center gap-5 text-sm">
            <a href="#how-it-works" className="hidden text-grey-600 transition hover:text-charcoal sm:inline">How it works</a>
            <a href="#start" className="hidden text-grey-600 transition hover:text-charcoal sm:inline">Talk to Abija</a>
            <Link href={authHref("sign-in", "")} className="font-semibold text-charcoal hover:text-orange-hover">Log in</Link>
            <a href="#start" onClick={() => setActiveTab("abija")} className="rounded-full bg-orange px-4 py-2.5 text-xs font-bold text-white transition hover:bg-orange-hover sm:px-5 sm:text-sm">
              Start with an idea <span aria-hidden="true">↗</span>
            </a>
          </nav>
        </div>
      </header>

      <section className="relative isolate overflow-hidden px-5 py-16 sm:px-8 sm:py-24 lg:py-28">
        <div aria-hidden="true" className="absolute -right-24 -top-32 -z-10 size-[34rem] rounded-full bg-orange/10 blur-3xl" />
        <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-orange/25 bg-white/70 px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-[0.14em] text-orange-hover">
              Built for Nigeria and Africa
            </p>
            <h1 className="max-w-3xl text-balance text-5xl font-extrabold leading-[0.98] tracking-[-0.075em] sm:text-6xl lg:text-7xl">
              Your business idea deserves a <em className="font-serif font-normal text-orange">real beginning.</em>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-grey-600 sm:text-lg sm:leading-8">
              Meet Abija, your AI business-building guide. Shape your idea, create a brand, and build your online presence in one guided workspace.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <a href="#start" onClick={() => setActiveTab("abija")} className="rounded-full bg-orange px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-orange-hover">
                Tell Abija your idea <span aria-hidden="true">→</span>
              </a>
              <a href="#how-it-works" className="text-sm font-bold text-charcoal hover:text-orange-hover">See how it works <span aria-hidden="true">↓</span></a>
            </div>
            <p className="mt-5 text-xs text-grey-600">You stay in control. Important work waits for your OK.</p>
          </div>

          <div className="relative mx-auto w-full max-w-xl">
            <div aria-hidden="true" className="absolute -inset-4 rounded-[2rem] bg-orange/10 blur-2xl" />
            <div className="relative overflow-hidden rounded-3xl border border-grey-200 bg-white p-5 shadow-[0_24px_70px_rgba(38,31,20,0.10)] sm:p-7">
              <div className="flex items-center gap-3 border-b border-grey-100 pb-5">
                <AbijaAvatar size="md" />
                <div>
                  <p className="font-bold">Abija</p>
                  <p className="text-xs text-grey-600">Your business-building guide</p>
                </div>
                <span className="ml-auto rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">READY WHEN YOU ARE</span>
              </div>
              <div className="py-6">
                <p className="max-w-[90%] rounded-2xl rounded-tl-sm bg-grey-100 px-4 py-3.5 text-sm leading-6 text-charcoal">
                  What business would you love to build? Start with a rough idea. We can work it out together.
                </p>
                <div className="mt-5 ml-auto max-w-[85%] rounded-2xl rounded-tr-sm bg-orange px-4 py-3.5 text-sm leading-6 text-white">
                  I want to start a natural skincare brand for busy mums in Lagos.
                </div>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-grey-200 bg-cream px-4 py-3 text-xs text-grey-600">
                <span>Your idea is the first step</span>
                <span aria-hidden="true" className="text-lg text-orange">↗</span>
              </div>
              <p className="mt-4 text-center text-[11px] text-grey-500">A glimpse of the guided experience — your conversation starts with your idea.</p>
            </div>
          </div>
        </div>
      </section>

      <section aria-label="Platform highlights" className="border-y border-grey-200 bg-white/60">
        <div className="mx-auto grid max-w-7xl gap-4 px-5 py-5 text-center text-xs font-semibold text-grey-600 sm:grid-cols-3 sm:px-8">
          <p>One idea, one guided workspace</p>
          <p>Brand and website built together</p>
          <p>Your approval before important steps</p>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-8 px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto max-w-7xl">
          <p className="text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">From first thought to launch</p>
          <div className="mt-4 grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <h2 className="max-w-xl text-4xl font-extrabold leading-[1.02] tracking-[-0.065em] sm:text-5xl">
                Build the pieces of your business <em className="font-serif font-normal text-orange">in one place.</em>
              </h2>
              <p className="mt-5 max-w-lg text-sm leading-7 text-grey-600">
                Instead of starting with a blank page, talk through what you want to make. Abija helps turn your brief into practical next steps.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                ["01", "Clarify the idea", "Describe what you want to offer and who you want to serve. Abija helps shape the brief."],
                ["02", "Shape your brand", "Bring your name, positioning, visual direction, and brand materials together."],
                ["03", "Build your presence", "Create a website experience that introduces your business to the right people."],
                ["04", "Review before launch", "See what is ready and approve important actions before anything goes live."],
              ].map(([number, title, description]) => (
                <article key={number} className="rounded-2xl border border-grey-200 bg-white p-5 sm:p-6">
                  <span className="inline-flex size-9 items-center justify-center rounded-full bg-orange/10 text-xs font-extrabold text-orange-hover">{number}</span>
                  <h3 className="mt-5 text-lg font-bold tracking-[-0.04em]">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-grey-600">{description}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="start" className="scroll-mt-8 bg-[#e9e8df] px-5 py-20 sm:px-8 sm:py-24">
        <div className="mx-auto grid max-w-7xl items-start gap-10 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="pt-2">
            <p className="text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">Your next step</p>
            <h2 className="mt-4 text-4xl font-extrabold leading-[1.02] tracking-[-0.065em] sm:text-5xl">
              Start with what’s on your <em className="font-serif font-normal text-orange">mind.</em>
            </h2>
            <p className="mt-5 max-w-md text-sm leading-7 text-grey-600">
              Explore how Cre8ive District works, or share your business idea with Abija. You can start with one sentence and add details later.
            </p>
            <div className="mt-7 flex flex-wrap gap-3 text-xs font-semibold text-grey-600">
              <span className="rounded-full border border-charcoal/10 bg-white/60 px-3 py-2">No business plan needed</span>
              <span className="rounded-full border border-charcoal/10 bg-white/60 px-3 py-2">Your OK before launch</span>
            </div>
          </div>

          <div className="overflow-hidden rounded-3xl border border-grey-200 bg-white shadow-[0_20px_60px_rgba(38,31,20,0.08)]">
            <div className="flex gap-1 border-b border-grey-200 bg-grey-100/60 p-2" aria-label="Choose a starting point">
              <button type="button" aria-pressed={activeTab === "overview"} onClick={() => setActiveTab("overview")} className={`flex-1 rounded-xl px-4 py-3 text-sm font-bold transition ${activeTab === "overview" ? "bg-white text-charcoal shadow-sm" : "text-grey-600 hover:bg-white/70"}`}>
                Explore the platform
              </button>
              <button type="button" aria-pressed={activeTab === "abija"} onClick={() => setActiveTab("abija")} className={`flex-1 rounded-xl px-4 py-3 text-sm font-bold transition ${activeTab === "abija" ? "bg-white text-charcoal shadow-sm" : "text-grey-600 hover:bg-white/70"}`}>
                Talk to Abija
              </button>
            </div>

            {activeTab === "overview" ? (
              <div className="p-6 sm:p-8">
                <div className="flex items-center gap-3">
                  <AbijaAvatar />
                  <div>
                    <h3 className="font-bold">A practical partner for your next move</h3>
                    <p className="mt-1 text-xs text-grey-600">Idea → brand → online presence → your approval</p>
                  </div>
                </div>
                <p className="mt-6 max-w-xl text-sm leading-7 text-grey-600">
                  Cre8ive District brings the early building blocks of a business into one workspace. Talk through your idea, develop your brand, and prepare a web presence with Abija guiding the process.
                </p>
                <ul className="mt-5 grid gap-3 text-sm text-charcoal sm:grid-cols-2">
                  {["Guided idea discovery", "Brand direction and assets", "A website for your business", "Clear review and approval steps"].map((item) => (
                    <li key={item} className="flex items-center gap-2"><span className="text-orange" aria-hidden="true">✓</span>{item}</li>
                  ))}
                </ul>
                <button type="button" onClick={() => setActiveTab("abija")} className="mt-8 rounded-full bg-orange px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-hover">
                  Start with your idea <span aria-hidden="true">→</span>
                </button>
              </div>
            ) : (
              <div className="p-6 sm:p-8">
                <div className="flex items-center gap-3">
                  <AbijaAvatar />
                  <div>
                    <h3 className="font-bold">Let’s start with your business idea</h3>
                    <p className="mt-1 text-xs text-grey-600">Abija will help you develop it in your workspace.</p>
                  </div>
                </div>
                <label htmlFor="business-idea" className="mt-6 block text-sm font-semibold">What would you like to build?</label>
                <textarea
                  id="business-idea"
                  value={idea}
                  onChange={(event) => setIdea(event.target.value.slice(0, 2000))}
                  maxLength={2000}
                  rows={4}
                  placeholder="For example: I want to start a natural skincare brand for busy mums in Lagos..."
                  className="mt-2 w-full resize-y rounded-xl border border-grey-200 bg-white px-4 py-3 text-sm leading-6 text-charcoal outline-none transition placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/20"
                />
                <div className="mt-2 flex justify-between text-[11px] text-grey-500">
                  <span>Your idea will be carried into your first Abija conversation.</span>
                  <span>{idea.length}/2000</span>
                </div>
                <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
                  {cleanIdea ? (
                    <Link href={signUpHref} className="inline-flex min-h-12 items-center justify-center rounded-full bg-orange px-6 py-3 text-sm font-bold text-white transition hover:bg-orange-hover">
                      Create account &amp; continue <span aria-hidden="true" className="ml-2">→</span>
                    </Link>
                  ) : (
                    <button type="button" disabled className="min-h-12 cursor-not-allowed rounded-full bg-orange/50 px-6 py-3 text-sm font-bold text-white">
                      Add your idea to continue
                    </button>
                  )}
                  <Link href={signInHref} className="text-center text-sm font-semibold text-orange-hover hover:underline">
                    Already have an account? Sign in
                  </Link>
                </div>
                <p className="mt-4 text-[11px] leading-5 text-grey-500">New here? Create an account. Returning? Sign in — your idea will stay with you either way.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      <footer className="border-t border-grey-200 px-5 py-7 sm:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 text-xs text-grey-600 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/" className="font-extrabold tracking-[-0.05em] text-charcoal">Cre<span className="text-orange">8</span>ive District</Link>
          <p>Built for business ideas taking shape across Nigeria and Africa.</p>
          <Link href={authHref("sign-in", "")} className="font-semibold hover:text-orange-hover">Log in</Link>
        </div>
      </footer>
    </main>
  );
}
