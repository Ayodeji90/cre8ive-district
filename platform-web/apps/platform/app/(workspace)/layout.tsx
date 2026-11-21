import type { ReactNode } from "react";

export default function WorkspaceLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <main id="content" className="h-screen w-screen overflow-hidden">
      {children}
    </main>
  );
}
