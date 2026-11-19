import { redirect } from "next/navigation";
import { auth } from "../lib/auth";
import { authQuery, type AuthSearchParams } from "../lib/auth-redirect";

interface PageProps {
  searchParams?: Promise<AuthSearchParams>;
}

/**
 * Compatibility entry point: old links and magic links still land on `/`.
 * Signed-in customers go to the workspace, everyone else goes to sign-in with the idea kept.
 */
export default async function PlatformHomePage({ searchParams }: PageProps) {
  const session = await auth();
  const params = searchParams ? await searchParams : undefined;

  // The workspace is the destination; only the idea needs to survive this hop.
  if (session?.user) redirect(`/workspace${authQuery({ idea: params?.idea })}`);
  redirect(`/sign-in${authQuery({ idea: params?.idea, next: "/workspace" })}`);
}
