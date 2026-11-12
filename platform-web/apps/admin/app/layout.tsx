import type { Metadata } from "next";
import { Toaster } from "@cre8ive/ui";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Admin — Cre8ive District", template: "%s | Cre8ive District" },
  description: "The Cre8ive District operations and designer review workspace.",
};

export default function AdminLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
