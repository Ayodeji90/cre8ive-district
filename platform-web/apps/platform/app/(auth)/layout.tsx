import type { ReactNode } from "react";

export default function AuthLayout({ children }: Readonly<{ children: ReactNode }>) {
  const marketingUrl = process.env.NEXT_PUBLIC_MARKETING_URL ?? "http://localhost:3000";
  return (
    <main className="grid min-h-screen place-items-center bg-cream px-5 py-12">
      <div className="w-full max-w-md">
        <a
          href={marketingUrl}
          className="mb-7 block text-center text-xl font-extrabold tracking-[-0.08em] text-charcoal"
        >
          Cre<span className="text-orange">8</span>ive District
        </a>
        {children}
        <p className="mt-6 text-center text-sm text-grey-600">
          Protected by secure sign-in. Your work stays yours.
        </p>
      </div>
    </main>
  );
}
