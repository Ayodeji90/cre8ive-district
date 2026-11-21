import Link from "next/link";

const exploreLinks = [
  ["How it works", "/#how-it-works"],
  ["What you get", "/#what-you-get"],
  ["Examples", "/#showcase"],
  ["FAQ", "/#faq"],
] as const;

const socials = [
  ["Instagram", "https://instagram.com/cre8ivedistrict"],
  ["LinkedIn", "https://www.linkedin.com/"],
] as const;

export function SiteFooter() {
  return (
    <footer className="border-t border-grey-200 bg-grey-100">
      <div className="mx-auto max-w-[72rem] px-6 pb-5 pt-14 md:px-8 lg:px-12">
        <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr]">
          <div>
            <Link href="/" aria-label="Cre8ive District home" className="text-base font-extrabold tracking-[-0.08em] text-charcoal">
              Cre<span className="text-orange">8</span>ive District
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-6 text-grey-600">
              An AI-powered brand and website launch platform for businesses in Nigeria. We’re still building — join the waitlist for early access.
            </p>
            <Link href="/#waitlist" className="mt-4 inline-flex text-sm font-bold text-orange-hover hover:underline">
              Join the waitlist <span aria-hidden="true">→</span>
            </Link>
          </div>

          <section aria-labelledby="footer-explore">
            <h2 id="footer-explore" className="mb-4 text-xs font-extrabold uppercase tracking-[0.12em] text-charcoal">Explore</h2>
            <ul className="grid gap-3">
              {exploreLinks.map(([label, href]) => (
                <li key={href}>
                  <Link className="text-sm text-grey-600 transition-colors hover:text-orange-hover" href={href}>{label}</Link>
                </li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="footer-contact">
            <h2 id="footer-contact" className="mb-4 text-xs font-extrabold uppercase tracking-[0.12em] text-charcoal">Contact</h2>
            <ul className="grid gap-3">
              <li>
                <a className="text-sm text-grey-600 transition-colors hover:text-orange-hover" href="mailto:hello@cre8ivedistrict.com">hello@cre8ivedistrict.com</a>
              </li>
              <li>
                <a className="text-sm text-grey-600 transition-colors hover:text-orange-hover" href="https://wa.me/2349038753287" target="_blank" rel="noreferrer">WhatsApp</a>
              </li>
            </ul>
          </section>
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-grey-200 pt-5 text-xs text-grey-600 sm:flex-row sm:items-center sm:justify-between">
          <span>© {new Date().getFullYear()} Cre8ive District · Nigeria</span>
          <nav aria-label="Social media" className="flex flex-wrap gap-4">
            {socials.map(([label, href]) => (
              <a key={label} href={href} target="_blank" rel="noreferrer" className="transition-colors hover:text-orange-hover">{label}</a>
            ))}
          </nav>
        </div>
      </div>
    </footer>
  );
}
