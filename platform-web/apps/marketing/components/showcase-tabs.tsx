"use client";

import { useState } from "react";

const tabs = ["Brand", "Social", "Website", "Materials"] as const;
type Tab = (typeof tabs)[number];

export function ShowcaseTabs() {
  const [selected, setSelected] = useState<Tab>("Brand");

  return (
    <div>
      <div role="group" aria-label="Aura Botanics example previews" className="mb-5 flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            aria-pressed={selected === tab}
            onClick={() => setSelected(tab)}
            className={`rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${selected === tab ? "border-charcoal bg-charcoal text-white" : "border-grey-200 bg-transparent text-grey-600 hover:bg-grey-100"}`}
          >
            {tab}
          </button>
        ))}
      </div>

      {selected === "Brand" && (
        <div className="grid min-h-[300px] gap-5 rounded-xl border border-grey-200 bg-[#eeeee8] p-5 sm:grid-cols-[0.9fr_1.1fr] sm:p-8">
          <div className="flex flex-col justify-between rounded-lg bg-[#f7f5ec] p-5 sm:p-7">
            <span className="text-[10px] font-extrabold tracking-[0.14em] text-grey-600">BRAND BOARD / EXAMPLE</span>
            <div>
              <div className="mb-4 grid size-14 place-items-center rounded-full border border-[#737b59] font-serif text-3xl text-[#737b59]">a.</div>
              <h3 className="font-serif text-3xl text-charcoal">Aura Botanics</h3>
              <p className="mt-1 text-sm text-grey-600">Studio concept · Identity direction</p>
            </div>
          </div>
          <div className="grid content-between gap-6 rounded-lg bg-white p-5 sm:p-7">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-grey-600">Colour palette</p>
              <div className="mt-3 flex flex-wrap gap-2"><span className="size-9 rounded-full bg-[#737b59]"/><span className="size-9 rounded-full bg-[#d59a55]"/><span className="size-9 rounded-full border border-grey-200 bg-[#ece6d2]"/><span className="size-9 rounded-full bg-[#393b31]"/></div>
            </div>
            <div className="grid grid-cols-2 gap-4 border-t border-grey-200 pt-4">
              <div><p className="text-xs font-bold uppercase tracking-[0.1em] text-grey-600">Heading</p><p className="mt-1 font-serif text-lg">Cormorant</p></div>
              <div><p className="text-xs font-bold uppercase tracking-[0.1em] text-grey-600">Body</p><p className="mt-1 text-lg">Plus Jakarta Sans</p></div>
              <p className="col-span-2 border-t border-grey-200 pt-3 text-sm italic text-grey-600">Care that comes naturally.</p>
            </div>
          </div>
        </div>
      )}

      {selected === "Social" && (
        <div className="grid min-h-[300px] place-items-center rounded-xl border border-grey-200 bg-[#e9e8df] p-6">
          <article className="w-full max-w-sm bg-[#f7f5ec] p-6 shadow-sm sm:p-8">
            <p className="text-[10px] font-extrabold tracking-[0.15em] text-[#737b59]">AURA BOTANICS</p>
            <h3 className="mt-8 font-serif text-4xl leading-[0.98] text-[#393b31]">Care that<br/><span className="italic text-[#737b59]">comes naturally.</span></h3>
            <p className="mt-8 border-t border-[#d9d7cc] pt-3 text-[10px] text-grey-600">Launch creative · Illustrative example</p>
          </article>
        </div>
      )}

      {selected === "Website" && (
        <div className="grid min-h-[300px] place-items-center rounded-xl border border-grey-200 bg-[#e8e5d9] p-5 sm:p-8">
          <article className="w-full max-w-2xl bg-[#faf8f2] p-5 shadow-sm sm:p-8">
            <div className="flex items-center gap-1 border-b border-grey-200 pb-3 text-[9px] text-orange-hover">● ● ● <span className="ml-2 text-grey-600">aurabotanics.example</span></div>
            <div className="py-8 sm:px-6 sm:py-10">
              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#737b59]">AURA BOTANICS</p>
              <h3 className="mt-4 font-serif text-4xl leading-[1.02] text-[#35392e] sm:text-5xl">Everyday care,<br/><span className="italic text-[#79805e]">rooted in nature.</span></h3>
              <p className="mt-4 max-w-sm text-sm leading-6 text-grey-600">A considered online home for a growing botanical care brand.</p>
              <span className="mt-6 inline-flex rounded-full bg-[#737b59] px-4 py-2 text-xs font-semibold text-white">Explore the collection ↗</span>
            </div>
          </article>
        </div>
      )}

      {selected === "Materials" && (
        <div className="grid min-h-[300px] place-items-center rounded-xl border border-grey-200 bg-[#eeeee8] p-6">
          <article className="w-full max-w-sm border border-[#d8d5c8] bg-[#f9f5e8] p-6 shadow-sm sm:p-8">
            <p className="text-[10px] font-extrabold tracking-[0.16em] text-[#737b59]">PALM &amp; PEPPER</p>
            <h3 className="mt-10 font-serif text-4xl leading-none text-[#393b31]">A taste of<br/><span className="italic text-[#9a4c2d]">something good.</span></h3>
            <p className="mt-8 border-t border-[#d8d5c8] pt-3 text-[9px] font-bold tracking-[0.13em] text-[#737b59]">JOLLOF · SUYA · SPICE</p>
          </article>
        </div>
      )}
      <p className="mt-3 text-xs text-grey-600">Illustrative studio concepts. These examples are not client work.</p>
    </div>
  );
}
