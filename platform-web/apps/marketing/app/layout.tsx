import type { Metadata } from "next";
import { Toaster } from "@cre8ive/ui";
import { SiteFooter } from "../components/site-footer";
import { SiteHeader } from "../components/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Cre8ive District — Build your brand", template: "%s | Cre8ive District" },
  description: "Cre8ive District is an AI-powered brand and website launch platform for businesses in Nigeria. Join the waitlist for early access.",
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
