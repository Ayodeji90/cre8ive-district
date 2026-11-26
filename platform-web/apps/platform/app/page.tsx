import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { auth } from "../lib/auth";
import { authQuery, readIdea, type AuthSearchParams } from "../lib/auth-redirect";
import { PlatformLanding } from "../components/landing/platform-landing";

interface PageProps {
  searchParams?: Promise<AuthSearchParams & { start?: string | string[] }>;
}

export const metadata: Metadata = {
  alternates: { canonical: "/" },
  openGraph: {
    title: "Cre8ive District — Build your business from the idea up",
    description: "Shape your business idea, brand, and online presence with Abija. Review every important step before it goes live.",
    url: "/",
  },
  twitter: {
    title: "Cre8ive District — Build your business from the idea up",
    description: "Shape your business idea, brand, and online presence with Abija. Review every important step before it goes live.",
  },
};

export default async function PlatformHomePage({ searchParams }: PageProps) {
  const session = await auth();
  const params = searchParams ? await searchParams : undefined;

  if (session?.user) redirect(`/workspace${authQuery({ idea: params?.idea })}`);
  return <PlatformLanding initialIdea={readIdea(params)} startWithIdea={params?.start === "idea"} />;
}
