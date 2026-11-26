import Link from "next/link";
import { PublicHeader } from "./public-header";

export interface ProductPageContent {
  title: string;
  eyebrow: string;
  headline: string;
  summary: string;
  status?: string;
  promise: string;
  steps: Array<{ title: string; description: string }>;
  cta: string;
}

export const PRODUCT_PAGES = {
  brand: {
    title: "Brand identity",
    eyebrow: "A brand that starts with your story",
    headline: "Give your business a clear identity from day one.",
    summary: "Share what you want to build and who you want to reach. Abija helps shape a brand direction that can carry through your launch.",
    promise: "Keep your brand thinking and launch materials connected in one workspace.",
    steps: [
      { title: "Start with your idea", description: "Explain your offer, audience, and the feeling you want your business to create." },
      { title: "Develop a direction", description: "Turn the brief into a considered name, positioning, and visual direction." },
      { title: "Review what is ready", description: "Explore your brand materials and give feedback before moving forward." },
    ],
    cta: "Start shaping your brand",
  },
  websites: {
    title: "Business websites",
    eyebrow: "A useful online home for your business",
    headline: "Bring your brand to life on the web.",
    summary: "Build a site around your real business details, with a clear path for customers to understand what you offer and how to reach you.",
    promise: "Your public site is part of the same guided journey as your brand—not a disconnected template.",
    steps: [
      { title: "Ground it in your business", description: "Use your offer, audience, and approved brand direction as the source for your site." },
      { title: "Create the key pages", description: "Bring together the information customers need to learn about and contact your business." },
      { title: "Review before publishing", description: "Check the content and presentation before your site is made public." },
    ],
    cta: "Start planning your website",
  },
  approvals: {
    title: "Founder control",
    eyebrow: "Automation with your OK",
    headline: "Move faster without giving up the final say.",
    summary: "Abija helps prepare the work. You can review important decisions and approve the next step before anything is published or sent.",
    promise: "Keep the review queue visible so drafts, approvals, and completed actions do not get mixed together.",
    steps: [
      { title: "See what needs review", description: "Find pending decisions in one place instead of chasing updates across tools." },
      { title: "Approve or ask for a change", description: "Choose whether a prepared item is ready to proceed or needs another pass." },
      { title: "Track what happens next", description: "See the difference between approved work and work that has actually been executed." },
    ],
    cta: "Start with your business idea",
  },
  growth: {
    title: "Growth",
    eyebrow: "What comes after launch",
    headline: "Build a foundation you can keep improving.",
    summary: "A launch is a beginning. We are shaping the next layer of Cre8ive District around helping founders understand what is working and choose a useful next move.",
    status: "In development",
    promise: "Live analytics, background outreach, social publishing, and automated growth recommendations are future capabilities—not available features today.",
    steps: [
      { title: "Get the essentials in place", description: "Start with a clear offer, a consistent brand, and a useful online presence." },
      { title: "Learn from real activity", description: "Future growth tools should use meaningful business signals, not guesswork." },
      { title: "Choose the next move", description: "Our direction is to help founders review opportunities and stay in control of what happens." },
    ],
    cta: "Start with your idea",
  },
} satisfies Record<string, ProductPageContent>;

export type ProductPageSlug = keyof typeof PRODUCT_PAGES;

export function getProductPage(slug: string): ProductPageContent | undefined {
  return Object.hasOwn(PRODUCT_PAGES, slug)
    ? PRODUCT_PAGES[slug as ProductPageSlug]
    : undefined;
}

export function ProductPage({ content }: { content: ProductPageContent }) {
  return (
    <main className="min-h-screen bg-cream text-charcoal">
      <PublicHeader />
      <section className="relative isolate overflow-hidden px-5 py-16 sm:px-8 sm:py-24 lg:py-28">
        <div aria-hidden="true" className="absolute -right-24 -top-32 -z-10 size-[34rem] rounded-full bg-orange/10 blur-3xl" />
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1fr_0.7fr] lg:items-center">
          <div>
            <p className="inline-flex rounded-full border border-orange/25 bg-white/70 px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-[0.14em] text-orange-hover">
              {content.eyebrow}
            </p>
            <h1 className="mt-5 max-w-3xl text-balance text-5xl font-extrabold leading-[0.98] tracking-[-0.075em] sm:text-6xl lg:text-7xl">
              {content.headline}
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-grey-600 sm:text-lg sm:leading-8">
              {content.summary}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link href="/?start=idea#idea-builder" className="rounded-full bg-orange px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-orange-hover">
                {content.cta} <span aria-hidden="true">→</span>
              </Link>
              <Link href="/#how-it-works" className="text-sm font-bold text-charcoal hover:text-orange-hover">
                See how it works <span aria-hidden="true">↓</span>
              </Link>
            </div>
            {content.status && (
              <p className="mt-5 inline-flex rounded-full bg-amber-100 px-3 py-1.5 text-xs font-bold text-amber-900">
                {content.status}
              </p>
            )}
          </div>
          <aside className="rounded-3xl border border-grey-200 bg-white p-6 shadow-[0_24px_70px_rgba(38,31,20,0.08)] sm:p-8">
            <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-orange-hover">The Cre8ive District approach</p>
            <p className="mt-4 text-xl font-bold leading-snug tracking-[-0.04em]">{content.promise}</p>
            <div className="mt-7 border-t border-grey-200 pt-5">
              <p className="text-xs font-semibold text-grey-600">Built around your idea</p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs font-bold">
                <span className="rounded-full bg-grey-100 px-3 py-2">Your business</span>
                <span aria-hidden="true" className="text-orange">→</span>
                <span className="rounded-full bg-grey-100 px-3 py-2">{content.title}</span>
                <span aria-hidden="true" className="text-orange">→</span>
                <span className="rounded-full bg-orange/10 px-3 py-2 text-orange-hover">Your OK</span>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="border-y border-grey-200 bg-white/60 px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto max-w-7xl">
          <p className="text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">A guided process</p>
          <h2 className="mt-3 max-w-3xl text-3xl font-extrabold leading-tight tracking-[-0.06em] sm:text-4xl">
            Start with the business. Build the next piece with intention.
          </h2>
          <div className="mt-8 grid gap-3 md:grid-cols-3">
            {content.steps.map((step, index) => (
              <article key={step.title} className="rounded-2xl border border-grey-200 bg-white p-5 sm:p-6">
                <span className="inline-flex size-9 items-center justify-center rounded-full bg-orange/10 text-xs font-extrabold text-orange-hover">
                  0{index + 1}
                </span>
                <h3 className="mt-5 text-lg font-bold tracking-[-0.04em]">{step.title}</h3>
                <p className="mt-2 text-sm leading-6 text-grey-600">{step.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 rounded-3xl bg-[#e9e8df] p-6 sm:flex-row sm:items-center sm:justify-between sm:p-10">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">Ready to begin?</p>
            <h2 className="mt-3 max-w-2xl text-3xl font-extrabold leading-tight tracking-[-0.06em]">
              Tell Abija what you want to build.
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-grey-600">
              You do not need a polished plan. Bring the idea and take the next step when you are ready.
            </p>
          </div>
          <Link href="/?start=idea#idea-builder" className="inline-flex shrink-0 items-center justify-center rounded-full bg-orange px-6 py-3.5 text-sm font-bold text-white transition hover:bg-orange-hover">
            Start with an idea <span aria-hidden="true" className="ml-2">→</span>
          </Link>
        </div>
      </section>
      <footer className="border-t border-grey-200 px-5 py-7 sm:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 text-xs text-grey-600 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/" className="font-extrabold tracking-[-0.05em] text-charcoal">Cre<span className="text-orange">8</span>ive District</Link>
          <p>Brand, web, and business building—guided by Abija.</p>
          <Link href="/sign-in?next=%2Fworkspace" className="font-semibold hover:text-orange-hover">Log in</Link>
        </div>
      </footer>
    </main>
  );
}
