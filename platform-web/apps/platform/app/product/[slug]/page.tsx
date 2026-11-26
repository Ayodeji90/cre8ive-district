import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getProductPage, PRODUCT_PAGES, ProductPage } from "../../../components/landing/product-pages";

interface ProductPageRouteProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return Object.keys(PRODUCT_PAGES).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: ProductPageRouteProps): Promise<Metadata> {
  const { slug } = await params;
  const content = getProductPage(slug);
  if (!content) return {};

  return {
    title: content.title,
    description: content.summary,
    alternates: { canonical: `/product/${slug}` },
    openGraph: {
      title: `${content.title} | Cre8ive District`,
      description: content.summary,
      url: `/product/${slug}`,
    },
    twitter: {
      title: `${content.title} | Cre8ive District`,
      description: content.summary,
    },
  };
}

export default async function ProductPageRoute({ params }: ProductPageRouteProps) {
  const { slug } = await params;
  const content = getProductPage(slug);
  if (!content) notFound();

  return <ProductPage content={content} />;
}
