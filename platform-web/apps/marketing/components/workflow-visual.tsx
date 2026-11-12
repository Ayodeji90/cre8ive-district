type VisualKind = "idea" | "brand" | "review" | "website" | "launch";

export function WorkflowVisual({ kind }: { kind: VisualKind }) {
  return (
    <div aria-hidden="true" className="relative mt-7 h-28 overflow-hidden rounded-lg border border-grey-200 bg-white p-3 shadow-sm">
      {kind === "idea" && (
        <div className="h-full rounded-md bg-cream p-3">
          <div className="mb-3 h-2 w-14 rounded-full bg-grey-200" />
          <div className="rounded-md border border-grey-200 bg-white p-2.5 text-[9px] text-grey-400">I want to start a business that...</div>
          <div className="ml-auto mt-2 grid size-5 place-items-center rounded-full bg-orange text-[10px] font-bold text-charcoal">↑</div>
        </div>
      )}
      {kind === "brand" && (
        <div className="flex h-full items-center gap-3 rounded-md bg-[#efeee7] p-3">
          <div className="grid size-12 shrink-0 place-items-center rounded-full border border-[#737b59] font-serif text-2xl text-[#737b59]">a.</div>
          <div className="min-w-0 flex-1">
            <div className="mb-2 h-2 w-16 rounded-full bg-charcoal/75" />
            <div className="h-1.5 w-24 max-w-full rounded-full bg-charcoal/15" />
            <div className="mt-3 flex gap-1.5"><i className="size-3 rounded-full bg-[#737b59]"/><i className="size-3 rounded-full bg-[#d59a55]"/><i className="size-3 rounded-full bg-[#e9e2cd]"/><i className="size-3 rounded-full bg-[#393b31]"/></div>
          </div>
        </div>
      )}
      {kind === "review" && (
        <div className="flex h-full items-center gap-3 rounded-md bg-cream p-3">
          <div className="grid size-10 shrink-0 place-items-center rounded-full bg-orange-light text-sm font-bold text-orange-hover">CD</div>
          <div className="min-w-0 flex-1">
            <div className="mb-2 h-2 w-24 rounded-full bg-charcoal/75" />
            <div className="h-1.5 w-full rounded-full bg-charcoal/15" />
            <div className="mt-2 h-1.5 w-3/4 rounded-full bg-charcoal/15" />
            <div className="mt-3 inline-flex rounded-full bg-[#2d8a4e]/10 px-2 py-1 text-[8px] font-semibold text-[#2d8a4e]">Review ready</div>
          </div>
        </div>
      )}
      {kind === "website" && (
        <div className="h-full rounded-md bg-[#f7f5ec] p-2.5">
          <div className="flex items-center gap-1 border-b border-grey-200 pb-1.5 text-[6px] text-orange-hover">● ● ● <span className="ml-2 text-grey-400">yourbrand.example</span></div>
          <p className="mt-2 font-serif text-sm leading-tight text-charcoal">Everyday care,<br/><span className="italic text-[#737b59]">rooted in nature.</span></p>
          <div className="mt-1 h-1 w-20 rounded-full bg-charcoal/15" />
        </div>
      )}
      {kind === "launch" && (
        <div className="flex h-full items-center justify-between rounded-md bg-[#25231e] px-4 text-white">
          <div><div className="mb-2 h-1.5 w-16 rounded-full bg-white/35"/><div className="font-serif text-base">Aura Botanics</div><div className="mt-1 text-[8px] text-white/60">Your online home is ready</div></div>
          <div className="grid size-9 place-items-center rounded-full bg-orange text-lg font-bold text-charcoal">↗</div>
        </div>
      )}
    </div>
  );
}
