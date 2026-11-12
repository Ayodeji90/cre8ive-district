import { Accordion, AccordionItem } from "@cre8ive/ui";
import { AbijaMascot } from "./abija-mascot";
import { AnimatedMascot } from "./animated-mascot";
import { ShowcaseTabs } from "./showcase-tabs";
import { WaitlistForm } from "./waitlist-form";
import { WorkflowVisual } from "./workflow-visual";
import { capabilities, homeFaqs, platformPrinciples, workflowSteps } from "../lib/home-content";

function SectionHeading({
  eyebrow,
  title,
  body,
  align = "left",
}: {
  eyebrow: string;
  title: React.ReactNode;
  body?: string;
  align?: "left" | "center";
}) {
  return (
    <div className={`mb-9 flex flex-col gap-4 md:mb-12 md:flex-row md:items-end md:justify-between ${align === "center" ? "text-center md:flex-col md:items-center" : ""}`}>
      <div>
        <p className="mb-3 text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">{eyebrow}</p>
        <h2 className="max-w-3xl text-3xl font-extrabold leading-[1.02] tracking-[-0.065em] text-charcoal sm:text-4xl lg:text-5xl">{title}</h2>
      </div>
      {body && <p className="max-w-md text-sm leading-6 text-grey-600 md:text-base">{body}</p>}
    </div>
  );
}

export function HomePage() {
  return (
    <main id="content">
      <section aria-labelledby="home-title" className="relative isolate flex min-h-[calc(100svh-76px)] items-center overflow-hidden bg-gradient-to-b from-cream via-cream to-grey-100 px-6 py-16 sm:py-20">
        <div aria-hidden="true" className="absolute inset-x-1/4 top-0 -z-10 h-96 rounded-full bg-orange/10 blur-3xl" />
        <div className="mx-auto flex w-full max-w-[72rem] flex-col items-center text-center">
          <AnimatedMascot />
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-orange/30 bg-orange-light px-3 py-1 text-[11px] font-extrabold uppercase tracking-[0.14em] text-orange-hover">
            <span aria-hidden="true" className="size-1.5 rounded-full bg-orange" /> Launching soon
          </p>
          <h1 id="home-title" className="w-full min-w-0 max-w-[1120px] text-balance text-[clamp(2.5rem,6vw,5rem)] font-extrabold leading-[0.99] tracking-[-0.085em] text-charcoal">
            Turn your idea into a <em className="font-serif font-normal tracking-[-0.065em] text-orange">real business.</em>
          </h1>
          <p className="mx-auto mb-7 mt-5 w-full min-w-0 max-w-[700px] text-balance text-base font-medium leading-relaxed text-charcoal sm:text-lg">
            Meet <span className="font-serif text-[1.12em] italic font-normal text-orange">Abija</span>, the AI employee who does all the work for you. We’re putting the finishing touches on the platform — join the waitlist for early access.
          </p>
          <div id="waitlist" className="w-full max-w-[640px] scroll-mt-28">
            <WaitlistForm id="waitlist-hero" source="hero" />
          </div>
          <p className="mt-4 w-full text-balance text-xs text-grey-600">You stay in control. Review the work before anything is published.</p>
        </div>
      </section>

      <section aria-label="Built for businesses in Nigeria and across Africa" className="border-y border-grey-200 bg-grey-100/70">
        <div className="mx-auto flex max-w-[72rem] gap-8 overflow-x-auto px-6 py-5 text-center text-xs text-grey-600 sm:justify-between md:px-8 lg:px-12">
          <p className="min-w-max flex-1">Built for businesses in Nigeria and across Africa</p>
          <p className="min-w-max flex-1">Brand and website in one guided journey</p>
          <p className="min-w-max flex-1">Human creative review when you need it</p>
        </div>
      </section>

      <section id="how-it-works" aria-labelledby="how-it-works-title" className="scroll-mt-24 px-6 py-20 md:px-8 md:py-28 lg:px-12">
        <div className="mx-auto max-w-[72rem]">
          <SectionHeading
            eyebrow="From idea to launch"
            title={<><span id="how-it-works-title">A clearer way to get your business started.</span></>}
            body="One guided process brings your brand, website, and launch essentials together."
          />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {workflowSteps.map((step, index) => (
              <article key={step.title} className="rounded-xl border border-grey-200 bg-white p-4 sm:p-5">
                <span className="inline-grid size-8 place-items-center rounded-full bg-orange-light text-xs font-extrabold text-orange-hover">0{index + 1}</span>
                <h3 className="mt-4 text-lg font-bold leading-tight tracking-[-0.04em] text-charcoal">{step.title}</h3>
                <p className="mt-2 min-h-[5rem] text-sm leading-5 text-grey-600">{step.body}</p>
                <WorkflowVisual kind={step.visual} />
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="what-you-get" aria-labelledby="capabilities-title" className="scroll-mt-24 bg-grey-100/75 px-6 py-20 md:px-8 md:py-28 lg:px-12">
        <div className="mx-auto max-w-[72rem]">
          <SectionHeading
            eyebrow="Made for your business"
            title={<><span id="capabilities-title">A connected brand, from the first impression to the website.</span></>}
            body="The platform is being built around the launch essentials African business owners need most."
          />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((item) => (
              <article key={item.label} className="min-h-56 border border-grey-200 bg-white/75 p-6 transition-transform hover:-translate-y-1 sm:p-7">
                <p className="text-[10px] font-extrabold tracking-[0.13em] text-orange-hover">{item.label}</p>
                <h3 className="mt-9 text-xl font-bold tracking-[-0.04em] text-charcoal">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-grey-600">{item.body}</p>
                {"note" in item && <p className="mt-3 text-xs font-semibold text-orange-hover">{item.note}</p>}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="showcase" aria-labelledby="showcase-title" className="scroll-mt-24 px-6 py-20 md:px-8 md:py-28 lg:px-12">
        <div className="mx-auto max-w-[72rem]">
          <SectionHeading
            eyebrow="One workspace, connected pieces"
            title={<><span id="showcase-title">Your brand should show up <em className="font-serif font-normal text-orange">as one business.</em></span></>}
            body="Keep your identity, website, launch assets, and review steps together instead of coordinating each piece by hand."
          />
          <ShowcaseTabs />
        </div>
      </section>

      <section aria-labelledby="principles-title" className="bg-[#e9e8df] px-6 py-20 md:px-8 md:py-24 lg:px-12">
        <div className="mx-auto max-w-[72rem]">
          <SectionHeading
            eyebrow="The platform principles"
            title={<><span id="principles-title">Tools that keep your business in charge.</span></>}
            body="The product plan brings automation together with clear customer control."
          />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {platformPrinciples.map((item) => (
              <article key={item.label} className="min-h-40 border-t border-charcoal/15 py-5">
                <p className="text-xs font-extrabold tracking-[0.12em] text-orange-hover">{item.label}</p>
                <h3 className="mt-5 text-xl font-bold tracking-[-0.04em] text-charcoal">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-grey-600">{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="stats-title" className="px-6 py-20 md:px-8 md:py-24 lg:px-12">
        <div className="mx-auto grid max-w-[72rem] gap-8 sm:grid-cols-2 lg:grid-cols-[1.5fr_repeat(3,1fr)] lg:items-center">
          <div className="sm:col-span-2 lg:col-span-1">
            <p className="mb-3 text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">A practical starting point</p>
            <h2 id="stats-title" className="text-3xl font-extrabold leading-[1.02] tracking-[-0.065em] text-charcoal sm:text-4xl">For the next business <em className="font-serif font-normal text-orange">you want to build.</em></h2>
          </div>
          {[
            ["01", "One guided brief"],
            ["02", "Brand and web, connected"],
            ["YOU", "In control of every approval"],
          ].map(([value, label]) => (
            <div key={value} className="grid gap-2 border-l border-grey-200 pl-5">
              <strong className="text-3xl font-extrabold tracking-[-0.06em] text-orange-hover">{value}</strong>
              <span className="text-sm text-grey-600">{label}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="faq" aria-labelledby="faq-title" className="scroll-mt-24 bg-grey-100/70 px-6 py-20 md:px-8 md:py-28 lg:px-12">
        <div className="mx-auto max-w-[870px]">
          <SectionHeading eyebrow="FAQ" title={<span id="faq-title">The questions business owners ask first.</span>} body="A few useful details before you begin." />
          <Accordion>
            {homeFaqs.map((item) => <AccordionItem key={item.question} title={item.question}>{item.answer}</AccordionItem>)}
          </Accordion>
        </div>
      </section>

      <section aria-labelledby="bottom-cta-title" className="px-6 py-16 md:px-8 md:py-24 lg:px-12">
        <div className="mx-auto grid max-w-[72rem] items-center gap-8 rounded-2xl bg-[#e9e8df] p-6 sm:p-10 lg:grid-cols-[1fr_auto] lg:p-14">
          <div>
            <AbijaMascot className="mb-3 size-16 drop-shadow-[0_6px_10px_rgba(93,57,29,0.12)]" />
            <p className="mb-3 text-xs font-extrabold uppercase tracking-[0.15em] text-orange-hover">Bring your idea</p>
            <h2 id="bottom-cta-title" className="max-w-3xl text-3xl font-extrabold leading-[1.02] tracking-[-0.065em] text-charcoal sm:text-4xl lg:text-5xl">Let’s build something <em className="font-serif font-normal text-orange">that feels like yours.</em></h2>
            <p className="mt-4 max-w-md text-sm leading-6 text-grey-600">We’re opening early access soon. Add your email and we’ll save you a spot.</p>
          </div>
          <div className="w-full lg:w-[460px]"><WaitlistForm id="waitlist-footer" source="footer" /></div>
        </div>
      </section>
    </main>
  );
}
