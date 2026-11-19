import type { Metadata } from "next";
import { Toaster } from "@cre8ive/ui";
import { SiteFooter } from "../components/site-footer";
import { SiteHeader } from "../components/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Cre8ive District — Build your brand", template: "%s | Cre8ive District" },
  description: "Shape your brand and online presence with guided, AI-assisted creative tools and human review. Cre8ive District is in development; join the waitlist for early access.",
  metadataBase: new URL("https://cre8ivedistrict.com"),
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: "/",
    siteName: "Cre8ive District",
    title: "Cre8ive District — Build your brand",
    description: "Shape your brand and online presence with guided, AI-assisted creative tools and human review.",
    images: [{ url: "/opengraph-image", width: 1200, height: 630, alt: "Cre8ive District — guided brand and website creation" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Cre8ive District — Build your brand",
    description: "Shape your brand and online presence with guided, AI-assisted creative tools and human review.",
    images: ["/opengraph-image"],
  },
};

export default function MarketingLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <a href="#content" className="absolute left-4 top-[-100px] z-50 rounded-md bg-white px-4 py-3 font-semibold text-charcoal shadow focus:top-4">
          Skip to content
        </a>
        <SiteHeader />
        {children}
        <SiteFooter />
        <Toaster />
      </body>
    </html>
  );
}
