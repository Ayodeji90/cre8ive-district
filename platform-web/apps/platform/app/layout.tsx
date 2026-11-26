import type { Metadata } from "next";
import { Toaster } from "@cre8ive/ui";
import { SessionProvider } from "next-auth/react";
import { ApiSessionBridge } from "../components/api-session-bridge";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Cre8ive District — Build your business from the idea up", template: "%s | Cre8ive District" },
  description: "Shape your business idea, brand, and online presence with Abija. Review every important step before it goes live.",
  metadataBase: new URL("https://cre8ivedistrict.app"),
  openGraph: {
    type: "website",
    siteName: "Cre8ive District",
    images: [{ url: "/opengraph-image", width: 1200, height: 630, alt: "Cre8ive District — build your business from the idea up" }],
  },
  twitter: {
    card: "summary_large_image",
    images: ["/opengraph-image"],
  },
};

export default function PlatformLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <SessionProvider>
          <ApiSessionBridge />
          {children}
          <Toaster />
        </SessionProvider>
      </body>
    </html>
  );
}
