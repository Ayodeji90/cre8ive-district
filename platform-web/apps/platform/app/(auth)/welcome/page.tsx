import { redirect } from "next/navigation";
import { auth } from "../../../lib/auth";
import { authQuery, resolvePostAuthPath, type AuthSearchParams } from "../../../lib/auth-redirect";

interface PageProps {
  searchParams?: Promise<AuthSearchParams>;
}

export default async function WelcomePage({ searchParams }: PageProps) {
  const params = searchParams ? await searchParams : undefined;
  if (!(await auth())?.user) redirect(`/sign-in${authQuery({ ...params, next: "/workspace" })}`);
  redirect(resolvePostAuthPath(params));
}
