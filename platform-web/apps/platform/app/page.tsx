import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "../lib/auth";

export default async function PlatformHomePage() {
  const session = await auth();
  if (!session?.user) redirect("/sign-in");

  return (
    <main id="content" className="min-h-screen px-6 py-10 sm:px-10">
      <header className="mx-auto flex max-w-content items-center justify-between border-b border-grey-200 pb-5">
        <Link href="/" className="text-lg font-extrabold tracking-[-0.08em] text-charcoal">Cre<span className="text-orange">8</span>ive District</Link>
        <span className="text-sm text-grey-600">{session.user.name ?? session.user.email}</span>
      </header>
      <section className="mx-auto max-w-content py-16 sm:py-24">
        <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-orange-hover">Your workspace</p>
        <h1 className="mt-4 max-w-3xl text-4xl font-extrabold leading-tight tracking-[-0.065em] text-charcoal sm:text-6xl">Good to have you here{session.user.name ? `, ${session.user.name.split(" ")[0]}` : ""}.</h1>
        <p className="mt-4 max-w-xl text-base leading-7 text-grey-600">Your business ideas, brand conversations, and launch work will live here. Start with an idea and Abija will help shape the next steps.</p>
        <a href={`${process.env.NEXT_PUBLIC_MARKETING_URL ?? "http://localhost:3000"}/#waitlist`} className="mt-8 inline-flex h-12 items-center gap-2 rounded-full bg-orange px-6 font-bold text-white hover:bg-orange-hover">Start with a business idea <span aria-hidden="true">↗</span></a>
      </section>
    </main>
  );
}
