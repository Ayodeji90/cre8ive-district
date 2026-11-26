import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { AuthForm } from "../../../components/auth-form";
import { auth } from "../../../lib/auth";
import { authQuery, resolvePostAuthPath, type AuthSearchParams } from "../../../lib/auth-redirect";

export const metadata: Metadata = { title: "Log in", robots: { index: false, follow: false } };

interface PageProps {
  searchParams?: Promise<AuthSearchParams>;
}

export default async function SignInPage({ searchParams }: PageProps) {
  const params = searchParams ? await searchParams : undefined;
  if ((await auth())?.user) redirect(resolvePostAuthPath(params));
  return (
    <AuthForm
      mode="sign-in"
      callbackUrl={resolvePostAuthPath(params)}
      switchHref={`/sign-up${authQuery(params)}`}
    />
  );
}
