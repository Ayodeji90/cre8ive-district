"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  ["How it works", "/#how-it-works"],
  ["What you get", "/#what-you-get"],
  ["Examples", "/#showcase"],
  ["FAQ", "/#faq"],
] as const;

function Brand() {
  return (
    <Link href="/" aria-label="Cre8ive District home" className="shrink-0 text-lg font-extrabold tracking-[-0.08em] text-charcoal">
      Cre<span className="text-orange">8</span>ive District
    </Link>
  );
}

export function SiteHeader() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const closeMenu = () => setMobileOpen(false);

  return (
    <header className="sticky top-0 z-40 border-b border-grey-200/80 bg-cream/95 backdrop-blur-xl">
      <div className="mx-auto flex min-h-[76px] max-w-[72rem] items-center justify-between gap-6 px-6 md:px-8 lg:px-12">
        <Brand />

        <nav aria-label="Main navigation" className="hidden items-center gap-1 lg:flex">
          {links.map(([label, href]) => (
            <Link key={href} href={href} className="rounded-md px-3 py-2 text-sm font-medium text-grey-600 transition-colors hover:text-charcoal">
              {label}
            </Link>
          ))}
          <Link href="/#waitlist" className="ml-3 inline-flex min-h-11 items-center gap-2 rounded-full bg-orange px-5 text-sm font-bold text-charcoal transition-colors hover:bg-orange-hover">
            Join waitlist <span aria-hidden="true">→</span>
          </Link>
        </nav>

        <button
          type="button"
          className="inline-flex size-11 shrink-0 items-center justify-center rounded-full border border-grey-200 text-sm font-semibold text-charcoal lg:hidden"
          aria-expanded={mobileOpen}
          aria-controls="mobile-navigation"
          onClick={() => setMobileOpen((open) => !open)}
        >
          <span className="sr-only">{mobileOpen ? "Close menu" : "Open menu"}</span>
          <span aria-hidden="true" className="text-xl leading-none">{mobileOpen ? "×" : "☰"}</span>
        </button>
      </div>

      <nav id="mobile-navigation" aria-label="Mobile navigation" hidden={!mobileOpen} className="absolute inset-x-0 top-full max-h-[calc(100svh-76px)] overflow-y-auto border-b border-grey-200 bg-cream px-6 pb-7 pt-3 shadow-lg lg:hidden">
        <div className="mx-auto grid max-w-[72rem] gap-1">
          {links.map(([label, href]) => (
            <Link key={href} href={href} onClick={closeMenu} className="rounded-md py-3 text-base font-medium text-charcoal">
              {label}
            </Link>
          ))}
          <Link href="/#waitlist" onClick={closeMenu} className="mt-4 inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-orange px-5 font-bold text-charcoal">
            Join waitlist <span aria-hidden="true">→</span>
          </Link>
        </div>
      </nav>
    </header>
  );
}
