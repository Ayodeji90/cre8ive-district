import { loadEnvConfig } from "@next/env";
import { resolve } from "node:path";

let loaded = false;

/**
 * Next.js only loads `.env*` files from the app directory, but this monorepo keeps a single
 * `.env` at the repo root. Server modules that read secrets at import time (Auth.js, the
 * adapter token) call this first so they see the same values as `next.config.ts`.
 */
export function loadRootEnv(): void {
  if (loaded) return;
  loaded = true;
  // `forceReload` is required: Next marks `process.env` as already processed while loading the
  // app directory (which has no `.env` files), so a plain call would be a no-op.
  loadEnvConfig(resolve(process.cwd(), "../../.."), process.env.NODE_ENV !== "production", console, true);
}
