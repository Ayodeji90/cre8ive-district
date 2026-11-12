import type { ReactNode } from "react";

export function AccordionItem({ title, children }: { title: string; children: ReactNode }) {
  return (
    <details className="group border-b border-grey-200 py-4">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-charcoal [&::-webkit-details-marker]:hidden">
        {title}<span aria-hidden="true" className="text-orange transition-transform group-open:rotate-45">+</span>
      </summary>
      <div className="pt-3 text-sm leading-6 text-grey-600">{children}</div>
    </details>
  );
}

export function Accordion({ children }: { children: ReactNode }) {
  return <div className="divide-y-0">{children}</div>;
}
