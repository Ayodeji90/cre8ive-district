import { redirect } from "next/navigation";
import { auth } from "../lib/auth";
import { AbijaWorkspace } from "../components/workspace/abija-workspace";

interface PageProps {
  searchParams?: Promise<{ idea?: string }>;
}

export default async function PlatformHomePage({ searchParams }: PageProps) {
  const session = await auth();
  if (!session?.user) redirect("/sign-in");

  const resolvedParams = searchParams ? await searchParams : {};
  const initialIdea = resolvedParams.idea;

  return (
    <main id="content" className="h-screen w-screen overflow-hidden">
      <AbijaWorkspace initialIdea={initialIdea} />
    </main>
  );
}
