import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { AuthForm } from "../../components/auth-form";
import { auth } from "../../lib/auth";

export const metadata: Metadata = { title: "Log in" };

export default async function SignInPage() {
  if ((await auth())?.user) redirect("/");
  return <AuthPage><AuthForm mode="sign-in" /></AuthPage>;
}

function AuthPage({ children }: Readonly<{ children: React.ReactNode }>) {
  return <main className="grid min-h-screen place-items-center bg-cream px-5 py-12"><div className="w-full max-w-md"><a href={process.env.NEXT_PUBLIC_MARKETING_URL ?? "http://localhost:3000"} className="mb-7 block text-center text-xl font-extrabold tracking-[-0.08em] text-charcoal">Cre<span className="text-orange">8</span>ive District</a>{children}<p className="mt-6 text-center text-sm text-grey-600">Protected by secure sign-in. Your work stays yours.</p></div></main>;
}
