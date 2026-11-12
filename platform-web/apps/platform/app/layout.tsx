import type { Metadata } from "next";
import { Toaster } from "@cre8ive/ui";
import { SessionProvider } from "next-auth/react";
import { ApiSessionBridge } from "../components/api-session-bridge";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Workspace — Cre8ive District", template: "%s | Cre8ive District" },
  description: "Your brand launch workspace with Abija.",
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
