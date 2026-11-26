"use client";

import Link from "next/link";

type MenuItem = {
  href: string;
  title: string;
  description: string;
};

const productLinks: MenuItem[] = [
  { href: "/product/brand", title: "Brand identity", description: "Shape your story and visual direction." },
  { href: "/product/websites", title: "Business websites", description: "Build a useful online home for your business." },
  { href: "/product/approvals", title: "Founder control", description: "Keep your OK in the workflow." },
  { href: "/product/growth", title: "Growth", description: "See what we are exploring next." },
];

const solutionLinks: MenuItem[] = [
  { href: "/?start=idea#idea-builder", title: "Starting with an idea", description: "Begin with what you know today." },
  { href: "/product/brand", title: "Building a brand", description: "Create a connected brand direction." },
  { href: "/product/websites", title: "Launching a website", description: "Bring your business online." },
];

const resourceLinks: MenuItem[] = [
  { href: "/#how-it-works", title: "How it works", description: "Follow the guided business-building journey." },
  { href: "/#faq", title: "Common questions", description: "Learn what to expect from Abija." },
  { href: "/#waitlist", title: "Early access", description: "Get updates as the platform takes shape." },
];

function NavigationDropdown({
  label,
  items,
  isHome,
}: {
  label: string;
  items: MenuItem[];
  isHome: boolean;
}) {
  return (
    <details className="group relative">
      <summary className="flex cursor-pointer list-none items-center gap-1.5 rounded-lg px-2 py-2 text-sm font-medium text-grey-600 transition hover:text-charcoal focus-visible:outline-2 focus-visible:outline-orange">
        {label}
        <span aria-hidden="true" className="text-[10px] transition group-open:rotate-180">⌄</span>
      </summary>
      <div className="absolute left-0 top-full z-50 mt-2 w-80 rounded-2xl border border-grey-200 bg-white p-2 shadow-[0_20px_60px_rgba(38,31,20,0.14)]">
        {items.map((item) => {
          const href = isHome && item.href.startsWith("/#") ? item.href.slice(1) : item.href;
          return (
            <Link key={item.title} href={href} className="block rounded-xl px-3 py-3 transition hover:bg-cream">
              <span className="flex items-center justify-between gap-3 text-sm font-bold text-charcoal">
                {item.title}
                {item.title === "Growth" && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[9px] font-bold text-amber-900">In development</span>}
              </span>
              <span className="mt-1 block text-xs leading-5 text-grey-500">{item.description}</span>
            </Link>
          );
        })}
      </div>
    </details>
  );
}

export function PublicHeader({
  isHome = false,
  onStart,
}: {
  isHome?: boolean;
  onStart?: () => void;
}) {
  const startHref = isHome ? "#idea-builder" : "/?start=idea#idea-builder";
  const howItWorksHref = isHome ? "#how-it-works" : "/#how-it-works";
  const faqHref = isHome ? "#faq" : "/#faq";
  const waitlistHref = isHome ? "#waitlist" : "/#waitlist";

  return (
    <header className="sticky top-0 z-40 border-b border-grey-200/80 bg-cream/90 backdrop-blur-md">
      <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between gap-4 px-5 sm:px-8">
        <Link href="/" className="shrink-0 text-lg font-extrabold tracking-[-0.07em]" aria-label="Cre8ive District home">
          Cre<span className="text-orange">8</span>ive District
        </Link>

        <nav aria-label="Main navigation" className="hidden items-center gap-1 lg:flex">
          <NavigationDropdown label="Product" items={productLinks} isHome={isHome} />
          <NavigationDropdown label="Solutions" items={solutionLinks} isHome={isHome} />
          <NavigationDropdown label="Resources" items={resourceLinks} isHome={isHome} />
          <Link href={howItWorksHref} className="rounded-lg px-2 py-2 text-sm font-medium text-grey-600 transition hover:text-charcoal">
            How it works
          </Link>
        </nav>

        <div className="flex shrink-0 items-center gap-3">
          <Link href="/sign-in?next=%2Fworkspace" className="hidden text-sm font-semibold text-charcoal transition hover:text-orange-hover sm:inline">
            Log in
          </Link>
          <a
            href={startHref}
            onClick={onStart}
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-full bg-charcoal px-4 text-xs font-bold text-white transition hover:bg-orange-hover sm:px-5 sm:text-sm"
          >
            Start with an idea <span aria-hidden="true">↗</span>
          </a>
          <details className="group relative lg:hidden">
            <summary aria-label="Open navigation menu" className="flex size-10 cursor-pointer list-none items-center justify-center rounded-full border border-grey-200 bg-white text-sm font-bold text-charcoal">
              <span aria-hidden="true">☰</span>
            </summary>
            <div className="absolute right-0 top-full z-50 mt-3 w-[min(90vw,22rem)] rounded-2xl border border-grey-200 bg-white p-3 shadow-[0_20px_60px_rgba(38,31,20,0.14)]">
              <p className="px-3 pb-2 pt-1 text-[10px] font-extrabold uppercase tracking-[0.15em] text-grey-500">Product</p>
              {productLinks.map((item) => (
                <Link key={item.title} href={item.href} className="block rounded-lg px-3 py-2.5 text-sm font-semibold hover:bg-cream">
                  {item.title}
                </Link>
              ))}
              <div className="my-2 border-t border-grey-100" />
              <Link href={howItWorksHref} className="block rounded-lg px-3 py-2.5 text-sm font-semibold hover:bg-cream">How it works</Link>
              <Link href={faqHref} className="block rounded-lg px-3 py-2.5 text-sm font-semibold hover:bg-cream">Common questions</Link>
              <Link href={waitlistHref} className="block rounded-lg px-3 py-2.5 text-sm font-semibold hover:bg-cream">Join the waitlist</Link>
              <Link href="/sign-in?next=%2Fworkspace" className="mt-2 block rounded-lg px-3 py-2.5 text-sm font-semibold text-orange-hover hover:bg-cream">Log in</Link>
            </div>
          </details>
        </div>
      </div>
    </header>
  );
}
