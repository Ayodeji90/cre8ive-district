import { redirect } from "next/navigation";
import { auth } from "../lib/auth";
import { authQuery, readIdea, type AuthSearchParams } from "../lib/auth-redirect";
import { PlatformLanding } from "../components/landing/platform-landing";

interface PageProps {
  searchParams?: Promise<AuthSearchParams>;
}

export default async function PlatformHomePage({ searchParams }: PageProps) {
  const session = await auth();
  const params = searchParams ? await searchParams : undefined;

  if (session?.user) redirect(`/workspace${authQuery({ idea: params?.idea })}`);
  return <PlatformLanding initialIdea={readIdea(params)} />;
}
