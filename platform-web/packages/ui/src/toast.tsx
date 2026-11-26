"use client";

import { Toaster as HotToaster, toast } from "react-hot-toast";

export { toast };

export function Toaster() {
  return <HotToaster position="top-right" toastOptions={{ duration: 4500 }} />;
}
