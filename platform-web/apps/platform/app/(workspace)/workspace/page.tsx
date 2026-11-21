import { redirect } from "next/navigation";
import { auth } from "../../../lib/auth";
import { authQuery, type AuthSearchParams } from "../../../lib/auth-redirect";
import { AbijaWorkspace } from "../../../components/workspace/abija-workspace";

interface PageProps {
  searchParams?: Promise<AuthSearchParams>;
}

export default async function WorkspacePage({ searchParams }: PageProps) {
  const session = await auth();
  const resolvedParams = searchParams ? await searchParams : undefined;
  if (!session?.user) {
    redirect(`/sign-in${authQuery({ ...resolvedParams, next: "/workspace" })}`);
  }

  const initialIdea =
    typeof resolvedParams?.idea === "string" ? resolvedParams.idea : resolvedParams?.idea?.[0];

  return <AbijaWorkspace initialIdea={initialIdea} />;
}
