import type { ReactNode } from "react";

export function Dropdown({ label, children }: { label: string; children: ReactNode }) {
  return (
    <details className="group relative">
      <summary className="flex cursor-pointer list-none items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-charcoal hover:bg-grey-100 [&::-webkit-details-marker]:hidden">
        {label}<span aria-hidden="true" className="text-grey-600 transition-transform group-open:rotate-180">⌄</span>
      </summary>
      <div className="absolute right-0 z-20 mt-2 min-w-48 rounded-lg border border-grey-200 bg-white p-2 shadow-lg">
        {children}
      </div>
    </details>
  );
}
