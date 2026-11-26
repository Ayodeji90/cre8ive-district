"use client";

import Link from "next/link";
import { useState } from "react";
import { AbijaAvatar } from "../chat/abija-avatar";
import { PublicHeader } from "./public-header";
import { WaitlistForm } from "./waitlist-form";

type LandingTab = "overview" | "abija";

const workflowSteps = [
  {
    title: "Start with what you know",
    description: "Tell Abija what you want to build, who it is for, and what you have figured out so far.",
    preview: "A useful brief begins with your words—not a blank form or a polished business plan.",
    label: "Your idea",
  },
  {
    title: "Shape your brand",
    description: "Develop a clear brand direction that can carry through your identity and online presence.",
    preview: "Review a considered direction for your business before moving on to the next piece.",
    label: "Brand direction",
  },
  {
    title: "Create your online home",
    description: "Prepare a business website using the details and brand direction you have reviewed.",
    preview: "Bring the offer, story, and next step together in a site designed for your business.",
    label: "Website draft",
  },
  {
    title: "Decide what happens next",
    description: "Review important work and keep the final say before anything consequential goes live.",
    preview: "A clear review step separates a prepared draft from an action you have approved.",
    label: "Your review",
  },
] as const;

const capabilities = [
  {
    href: "/product/brand",
    eyebrow: "Brand identity",
    title: "A clear identity for the business you want to build.",
    description: "Shape the story, positioning, and visual direction behind your next move.",
    visual: "brand",
  },
  {
    href: "/product/websites",
    eyebrow: "Business websites",
    title: "A useful online home, grounded in your business.",
    description: "Bring your offer and brand together in a website customers can understand.",
    visual: "website",
  },
  {
    href: "/product/approvals",
    eyebrow: "Founder control",
    title: "Automation that still waits for your OK.",
    description: "Review important work and see what is a draft, approved, or actually done.",
    visual: "approval",
  },
] as const;

const questions = [
  {
    question: "What is Cre8ive District?",
    answer: "Cre8ive District is a guided business-building platform for entrepreneurs in Nigeria and across Africa. Abija helps you move from an early idea toward a clear brand and online presence.",
  },
  {
    question: "Do I need a detailed business plan?",
    answer: "No. Start with a rough description of what you would like to build. You can add details and refine the idea as you go.",
  },
  {
    question: "Will Abija publish or send things without asking?",
    answer: "Important actions are designed to wait for your review and approval. A draft or an approval is not the same as a completed action.",
  },
  {
    question: "How much does it cost?",
    answer: "Plans and pricing have not been published yet. Join the waitlist and we will share updates as early access takes shape.",
  },
] as const;

function authHref(mode: "sign-in" | "sign-up", idea: string) {
  const query = new URLSearchParams({ next: "/workspace" });
  if (idea) query.set("idea", idea);
  return `/${mode}?${query.toString()}`;
}

function CapabilityVisual({ kind }: { kind: (typeof capabilities)[number]["visual"] }) {
  if (kind === "brand") {
    return (
      <div aria-hidden="true" className="flex h-44 items-end gap-3 overflow-hidden rounded-2xl bg-[#f3eee4] p-5">
        <div className="flex size-20 items-center justify-center rounded-full bg-[#d36a3b] text-2xl font-bold text-white">A</div>
        <div className="flex-1 rounded-xl bg-white p-4 shadow-sm">
          <div className="h-2 w-14 rounded-full bg-[#d36a3b]" />
          <div className="mt-3 h-2 w-24 rounded-full bg-charcoal/15" />
          <div className="mt-2 h-2 w-16 rounded-full bg-charcoal/10" />
          <div className="mt-4 flex gap-1.5">
            <span className="size-4 rounded-full bg-[#d36a3b]" />
            <span className="size-4 rounded-full bg-[#283b32]" />
            <span className="size-4 rounded-full bg-[#e7b76c]" />
            <span className="size-4 rounded-full bg-[#e8dfd1]" />
          </div>
        </div>
      </div>
    );
  }

  if (kind === "website") {
    return (
      <div aria-hidden="true" className="h-44 overflow-hidden rounded-2xl bg-[#e5edf0] p-4">
        <div className="h-full overflow-hidden rounded-xl border border-grey-200 bg-white shadow-sm">
          <div className="flex h-7 items-center gap-1 border-b border-grey-100 px-3">
            <span className="size-1.5 rounded-full bg-[#e27c5a]" />
            <span className="size-1.5 rounded-full bg-[#e4bf70]" />
            <span className="size-1.5 rounded-full bg-[#79a889]" />
          </div>
          <div className="grid h-full grid-cols-[1.1fr_0.9fr] gap-3 p-4">
            <div className="pt-2">
              <div className="h-2 w-20 rounded-full bg-charcoal/15" />
              <div className="mt-3 h-3 w-full rounded-full bg-charcoal/75" />
              <div className="mt-2 h-3 w-4/5 rounded-full bg-charcoal/75" />
              <div className="mt-3 h-2 w-full rounded-full bg-charcoal/10" />
              <div className="mt-2 h-2 w-3/4 rounded-full bg-charcoal/10" />
              <div className="mt-4 h-6 w-20 rounded-full bg-orange" />
            </div>
            <div className="rounded-lg bg-[#d6e5dc]" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div aria-hidden="true" className="flex h-44 items-center justify-center rounded-2xl bg-[#f2e8de] p-5">
      <div className="w-full max-w-sm rounded-xl border border-grey-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-wider text-grey-500">Review item</span>
          <span className="rounded-full bg-amber-50 px-2 py-1 text-[9px] font-bold text-amber-800">Needs your OK</span>
        </div>
        <div className="mt-4 h-2 w-3/4 rounded-full bg-charcoal/60" />
        <div className="mt-2 h-2 w-full rounded-full bg-charcoal/10" />
        <div className="mt-2 h-2 w-2/3 rounded-full bg-charcoal/10" />
        <div className="mt-4 flex gap-2">
          <span className="rounded-full bg-orange px-3 py-1.5 text-[9px] font-bold text-white">Approve</span>
          <span className="rounded-full border border-grey-200 px-3 py-1.5 text-[9px] font-bold text-grey-600">Request a change</span>
        </div>
      </div>
    </div>
  );
}

export function PlatformLanding({
  initialIdea = "",
  startWithIdea = false,
}: {
  initialIdea?: string;
  startWithIdea?: boolean;
}) {
  const [idea, setIdea] = useState(initialIdea.trim().slice(0, 2000));
  const [activeTab, setActiveTab] = useState<LandingTab>(
    initialIdea.trim() || startWithIdea ? "abija" : "overview",
  );
  const [activeStep, setActiveStep] = useState(0);
  const cleanIdea = idea.trim();
  const signUpHref = authHref("sign-up", cleanIdea);
  const signInHref = authHref("sign-in", cleanIdea);

  return (
    <main className="min-h-screen bg-cream text-charcoal">
      <PublicHeader isHome onStart={() => setActiveTab("abija")} />

      <section id="idea-builder" className="relative isolate overflow-hidden bg-[#f4f4ec] px-5 pb-20 pt-14 sm:px-8 sm:pb-24 sm:pt-20 lg:min-h-[690px] lg:pt-24">
        <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_50%_0%,rgba(255,111,42,0.17),transparent_58%),linear-gradient(180deg,#f4f4ec_0%,#fbf8f1_60%,#f2eee3_100%)]" />
        <div aria-hidden="true" className="absolute -bottom-48 left-1/2 -z-10 size-[34rem] -translate-x-1/2 rounded-full bg-orange/10 blur-3xl" />
        <div className="mx-auto flex max-w-5xl flex-col items-center text-center">
          <div className="mb-5">
            <AbijaAvatar size="md" showStatus={false} />
          </div>
          <p className="text-xs font-extrabold uppercase tracking-[0.18em] text-orange-hover">
            Your AI business-building guide
          </p>
          <h1 className="mt-4 max-w-4xl text-balance text-5xl font-extrabold leading-[0.99] tracking-[-0.075em] sm:text-6xl lg:text-7xl">
            Start with an idea.
            <span className="block font-serif font-normal italic text-orange">Build from there.</span>
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-grey-600 sm:text-lg sm:leading-8">
            Meet Abija. Shape your business, create a brand, and build your online presence—with you in control of what happens next.
          </p>

          <div className="mt-8 w-full max-w-2xl rounded-[1.75rem] border border-charcoal/10 bg-white p-3 text-left shadow-[0_24px_80px_rgba(54,44,31,0.12)] sm:p-4">
            <div className="flex flex-wrap items-center justify-between gap-3 px-2 pb-2 sm:px-3">
              <div className="flex items-center gap-2.5">
                <AbijaAvatar size="sm" showStatus={false} />
                <div>
                  <p className="text-sm font-bold">Talk to Abija</p>
                  <p className="text-[11px] text-grey-500">
                    {activeTab === "abija" ? "Your idea starts the conversation." : "No business plan needed to begin."}
                  </p>
                </div>
              </div>
              <div role="group" aria-label="Choose a starting point" className="flex rounded-full bg-grey-100 p-1">
                <button
                  type="button"
                  aria-pressed={activeTab === "overview"}
                  onClick={() => setActiveTab("overview")}
                  className={`rounded-full px-3 py-1.5 text-[11px] font-bold transition ${activeTab === "overview" ? "bg-white text-charcoal shadow-sm" : "text-grey-500 hover:text-charcoal"}`}
                >
                  Explore
                </button>
                <button
                  type="button"
                  aria-pressed={activeTab === "abija"}
                  onClick={() => setActiveTab("abija")}
                  className={`rounded-full px-3 py-1.5 text-[11px] font-bold transition ${activeTab === "abija" ? "bg-white text-charcoal shadow-sm" : "text-grey-500 hover:text-charcoal"}`}
                >
                  Talk to Abija
                </button>
              </div>
            </div>
            <label htmlFor="business-idea" className="sr-only">What would you like to build?</label>
            <textarea
              id="business-idea"
              value={idea}
              onChange={(event) => setIdea(event.target.value.slice(0, 2000))}
              maxLength={2000}
              rows={3}
              placeholder="I want to build a business that..."
              className="w-full resize-y rounded-2xl border-0 bg-transparent px-3 py-3 text-base leading-7 text-charcoal outline-none placeholder:text-grey-400 focus:ring-2 focus:ring-orange/30 sm:px-4"
            />
            <div className="flex flex-col gap-3 border-t border-grey-100 px-2 pt-3 sm:flex-row sm:items-center sm:justify-between sm:px-3">
              <p className="text-xs text-grey-500">
                {cleanIdea ? `${idea.length}/2000 characters` : "Start rough. You can refine it together."}
              </p>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <Link href={signInHref} className="text-center text-xs font-semibold text-grey-600 hover:text-orange-hover">
                  Already have an account? Log in
                </Link>
                {cleanIdea ? (
                  <Link href={signUpHref} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-orange px-5 text-sm font-bold text-white transition hover:bg-orange-hover">
                    Send to Abija <span aria-hidden="true">↗</span>
                  </Link>
                ) : (
                  <button type="button" disabled className="min-h-11 cursor-not-allowed rounded-full bg-orange/50 px-5 text-sm font-bold text-white">
                    Add your idea to begin
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-[11px] text-grey-500">
            <span>Need a starting point?</span>
            <button type="button" onClick={() => setIdea("I want to start a food business in Abuja.")} className="rounded-full border border-charcoal/10 bg-white/70 px-3 py-1.5 font-semibold text-grey-600 transition hover:border-orange/40 hover:text-orange-hover">
              A food business in Abuja
            </button>
            <button type="button" onClick={() => setIdea("I want to build a skincare brand for customers in Lagos.")} className="rounded-full border border-charcoal/10 bg-white/70 px-3 py-1.5 font-semibold text-grey-600 transition hover:border-orange/40 hover:text-orange-hover">
              A skincare brand in Lagos
            </button>
          </div>
          <a href="#how-it-works" className="mt-8 text-xs font-bold text-charcoal underline decoration-charcoal/20 underline-offset-4 transition hover:text-orange-hover">
            See how Cre8ive District works ↓
          </a>
        </div>
      </section>

      <section aria-label="Cre8ive District principles" className="border-y border-grey-200 bg-white">
        <div className="mx-auto grid max-w-7xl gap-3 px-5 py-5 text-center text-xs font-semibold text-grey-600 sm:grid-cols-3 sm:px-8">
          <p>Designed for founders in Nigeria and across Africa</p>
          <p>Idea, brand, and website in one guided journey</p>
          <p>Important actions wait for your OK</p>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-20 px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
            <div>
              <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">From idea to online presence</p>
              <h2 className="mt-4 max-w-xl text-4xl font-extrabold leading-[1.02] tracking-[-0.065em] sm:text-5xl">
                One idea. A clear next step.
              </h2>
            </div>
            <p className="max-w-2xl text-sm leading-7 text-grey-600 sm:text-base">
              Cre8ive District brings the early building blocks of a business into one place. Follow the journey at your pace and review important work as it takes shape.
            </p>
          </div>

          <div className="mt-10 grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
            <div role="group" aria-label="Business-building steps" className="flex flex-col gap-2">
              {workflowSteps.map((step, index) => (
                <button
                  key={step.label}
                  type="button"
                  aria-pressed={activeStep === index}
                  onClick={() => setActiveStep(index)}
                  className={`grid grid-cols-[42px_1fr] gap-4 rounded-2xl border p-4 text-left transition sm:p-5 ${activeStep === index ? "border-orange/40 bg-white shadow-[0_12px_35px_rgba(38,31,20,0.06)]" : "border-transparent hover:border-grey-200 hover:bg-white/70"}`}
                >
                  <span className={`flex size-10 items-center justify-center rounded-full text-xs font-extrabold ${activeStep === index ? "bg-orange text-white" : "bg-grey-100 text-grey-600"}`}>
                    0{index + 1}
                  </span>
                  <span>
                    <span className="block text-base font-bold tracking-[-0.03em]">{step.title}</span>
                    <span className="mt-1 block text-sm leading-6 text-grey-600">{step.description}</span>
                  </span>
                </button>
              ))}
            </div>

            <div className="relative overflow-hidden rounded-[1.75rem] border border-grey-200 bg-[#e8eee8] p-4 sm:p-7">
              <div aria-hidden="true" className="absolute -right-20 -top-20 size-64 rounded-full bg-orange/10 blur-3xl" />
              <div className="relative rounded-2xl border border-white/80 bg-white/90 p-5 shadow-[0_20px_70px_rgba(38,31,20,0.08)] sm:p-7">
                <div className="flex items-center justify-between gap-3 border-b border-grey-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <AbijaAvatar size="sm" showStatus={false} />
                    <div>
                      <p className="text-sm font-bold">Abija workspace</p>
                      <p className="text-[10px] text-grey-500">An illustrative workflow preview</p>
                    </div>
                  </div>
                  <span className="rounded-full bg-orange/10 px-3 py-1.5 text-[10px] font-bold text-orange-hover">
                    {workflowSteps[activeStep].label}
                  </span>
                </div>
                <div className="grid gap-6 py-6 sm:grid-cols-[1fr_0.8fr] sm:items-center">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-orange-hover">Step 0{activeStep + 1}</p>
                    <h3 className="mt-3 text-2xl font-extrabold leading-tight tracking-[-0.05em]">
                      {workflowSteps[activeStep].title}
                    </h3>
                    <p className="mt-3 text-sm leading-6 text-grey-600">{workflowSteps[activeStep].preview}</p>
                  </div>
                  <div aria-hidden="true" className="rounded-2xl bg-cream p-4">
                    <div className="flex items-center gap-2">
                      <span className="size-7 rounded-full bg-orange/15" />
                      <span className="h-2 w-24 rounded-full bg-charcoal/15" />
                    </div>
                    <div className="mt-4 space-y-2">
                      <div className="h-2 w-full rounded-full bg-charcoal/10" />
                      <div className="h-2 w-5/6 rounded-full bg-charcoal/10" />
                      <div className="h-2 w-2/3 rounded-full bg-charcoal/10" />
                    </div>
                    <div className="mt-5 flex items-center justify-between rounded-xl border border-grey-200 bg-white px-3 py-2.5">
                      <span className="text-[10px] font-semibold text-grey-600">Your next step</span>
                      <span className="text-sm font-bold text-orange">→</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1.5" aria-hidden="true">
                  {workflowSteps.map((step, index) => (
                    <span key={step.label} className={`h-1.5 flex-1 rounded-full ${index <= activeStep ? "bg-orange" : "bg-grey-100"}`} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="product" className="border-y border-grey-200 bg-white px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-3xl">
            <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">A connected foundation</p>
            <h2 className="mt-4 text-4xl font-extrabold leading-[1.02] tracking-[-0.065em] sm:text-5xl">
              Build the pieces your business needs to get started.
            </h2>
            <p className="mt-5 text-sm leading-7 text-grey-600 sm:text-base">
              Start with a thoughtful brand, bring it to the web, and keep your say in what happens next.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {capabilities.map((capability) => (
              <article key={capability.href} className="flex flex-col rounded-3xl border border-grey-200 bg-cream/55 p-4 transition hover:-translate-y-1 hover:border-orange/30 hover:shadow-[0_18px_48px_rgba(38,31,20,0.08)] sm:p-5">
                <CapabilityVisual kind={capability.visual} />
                <div className="flex flex-1 flex-col p-2 pt-5">
                  <p className="text-[10px] font-extrabold uppercase tracking-[0.15em] text-orange-hover">{capability.eyebrow}</p>
                  <h3 className="mt-3 text-xl font-bold leading-snug tracking-[-0.045em]">{capability.title}</h3>
                  <p className="mt-3 flex-1 text-sm leading-6 text-grey-600">{capability.description}</p>
                  <Link href={capability.href} className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-charcoal transition hover:text-orange-hover">
                    Explore {capability.eyebrow.toLowerCase()} <span aria-hidden="true">→</span>
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-20 sm:px-8 sm:py-24">
        <div className="mx-auto grid max-w-7xl gap-8 rounded-[2rem] bg-[#262b26] p-7 text-white sm:p-10 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-[#ffb27a]">Your business, your call</p>
            <h2 className="mt-4 max-w-3xl text-3xl font-extrabold leading-tight tracking-[-0.06em] sm:text-4xl">
              Abija helps prepare the work. You decide what is ready.
            </h2>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-white/70">
              Drafts, approvals, and completed actions are different things. Important steps should be clear before anything goes public.
            </p>
          </div>
          <Link href="/product/approvals" className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-white px-5 text-sm font-bold text-charcoal transition hover:bg-[#f4e9dc]">
            How approvals work <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      <section id="faq" className="scroll-mt-20 border-y border-grey-200 bg-white px-5 py-20 sm:px-8 sm:py-28">
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.7fr_1.3fr]">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">Good questions</p>
            <h2 className="mt-4 text-4xl font-extrabold leading-[1.02] tracking-[-0.065em] sm:text-5xl">
              Before you get started.
            </h2>
            <p className="mt-5 max-w-sm text-sm leading-7 text-grey-600">
              If your question is about your own business idea, you can bring it to Abija and work through it together.
            </p>
          </div>
          <div className="divide-y divide-grey-200 border-y border-grey-200">
            {questions.map((item, index) => (
              <details key={item.question} open={index === 0} className="group py-5">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-base font-bold">
                  {item.question}
                  <span aria-hidden="true" className="text-xl font-normal text-orange transition group-open:rotate-45">+</span>
                </summary>
                <p className="max-w-2xl pt-3 text-sm leading-6 text-grey-600">{item.answer}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-20 sm:px-8 sm:py-24">
        <div className="mx-auto flex max-w-7xl flex-col items-center rounded-[2rem] bg-[#f1e2d4] px-6 py-14 text-center sm:px-10 sm:py-20">
          <AbijaAvatar size="md" showStatus={false} />
          <p className="mt-5 text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">Your idea can start here</p>
          <h2 className="mt-4 max-w-3xl text-4xl font-extrabold leading-tight tracking-[-0.065em] sm:text-5xl">
            What would you like to build?
          </h2>
          <p className="mt-4 max-w-xl text-sm leading-7 text-grey-600">
            Tell Abija the first thing on your mind. You can create an account or log in and take it from there.
          </p>
          <a href="#idea-builder" onClick={() => setActiveTab("abija")} className="mt-7 inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-orange px-6 text-sm font-bold text-white transition hover:bg-orange-hover">
            Start with your idea <span aria-hidden="true">↑</span>
          </a>
        </div>
      </section>

      <section id="waitlist" className="scroll-mt-20 border-t border-grey-200 bg-white px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">Keep in touch</p>
            <h2 className="mt-4 max-w-xl text-3xl font-extrabold leading-tight tracking-[-0.06em] sm:text-4xl">
              Get updates as early access takes shape.
            </h2>
            <p className="mt-4 max-w-md text-sm leading-7 text-grey-600">
              Share your email to join the waitlist. Add your business idea if you’d like us to understand what you’re planning.
            </p>
          </div>
          <WaitlistForm />
        </div>
      </section>

      <footer className="border-t border-grey-200 px-5 py-8 sm:px-8">
        <div className="mx-auto grid max-w-7xl gap-8 sm:grid-cols-[1fr_auto_auto] sm:items-start">
          <div>
            <Link href="/" className="text-base font-extrabold tracking-[-0.07em]" aria-label="Cre8ive District home">
              Cre<span className="text-orange">8</span>ive District
            </Link>
            <p className="mt-3 max-w-sm text-xs leading-5 text-grey-600">
              A guided business-building experience for founders in Nigeria and across Africa.
            </p>
          </div>
          <div className="flex flex-col gap-2 text-xs text-grey-600">
            <span className="mb-1 font-bold text-charcoal">Explore</span>
            <Link href="/product/brand" className="hover:text-orange-hover">Brand identity</Link>
            <Link href="/product/websites" className="hover:text-orange-hover">Business websites</Link>
            <Link href="/product/approvals" className="hover:text-orange-hover">Founder control</Link>
          </div>
          <div className="flex flex-col gap-2 text-xs text-grey-600">
            <span className="mb-1 font-bold text-charcoal">Get started</span>
            <a href="#idea-builder" onClick={() => setActiveTab("abija")} className="hover:text-orange-hover">Talk to Abija</a>
            <a href="#how-it-works" className="hover:text-orange-hover">How it works</a>
            <a href="#waitlist" className="hover:text-orange-hover">Join the waitlist</a>
            <Link href={authHref("sign-in", "")} className="hover:text-orange-hover">Log in</Link>
          </div>
        </div>
        <div className="mx-auto mt-8 max-w-7xl border-t border-grey-200 pt-4 text-[11px] text-grey-500">
          © {new Date().getFullYear()} Cre8ive District
        </div>
      </footer>
    </main>
  );
}
