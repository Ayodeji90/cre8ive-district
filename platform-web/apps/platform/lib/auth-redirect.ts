/**
 * Shared handoff rules for the public site → auth → workspace journey.
 *
 * `idea` is free text the customer wrote on the public site. It is carried as a query param
 * through sign-in and seeds the first conversation. `next`/`callbackUrl` are reduced to a
 * same-origin path so they can never be used as an open redirect.
 */

export interface AuthSearchParams {
  idea?: string | string[];
  next?: string | string[];
  callbackUrl?: string | string[];
}

const MAX_IDEA_LENGTH = 2000;
const RELATIVE_BASE = "https://cre8ive.invalid";

function firstValue(value?: string | string[]): string | undefined {
  const raw = Array.isArray(value) ? value[0] : value;
  return typeof raw === "string" ? raw : undefined;
}

export function readIdea(params?: AuthSearchParams): string | undefined {
  const idea = firstValue(params?.idea)?.trim().slice(0, MAX_IDEA_LENGTH);
  return idea ? idea : undefined;
}

/** Reduces a relative or absolute URL to a path on this app, or `/` when it is not usable. */
export function toSafePath(value?: string): string {
  if (!value) return "/";
  // A protocol-relative value like `//evil.com/x` is another origin, not a path on this app.
  if (value.startsWith("//") || value.startsWith("/\\")) return "/";
  try {
    const url = new URL(value, RELATIVE_BASE);
    // URL accepts non-HTTP schemes such as `javascript:`; their pathname is not
    // guaranteed to be an app-relative route and must not become a callback URL.
    if (!url.pathname.startsWith("/")) return "/";
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return "/";
  }
}

/** The path to land on after authentication, with the idea attached if it is not already there. */
export const DEFAULT_POST_AUTH_PATH = "/workspace";

export function resolvePostAuthPath(params?: AuthSearchParams): string {
  const idea = readIdea(params);
  const requested = firstValue(params?.callbackUrl) ?? firstValue(params?.next);
  const path = requested ? toSafePath(requested) : DEFAULT_POST_AUTH_PATH;
  if (!idea) return path;

  const url = new URL(path, RELATIVE_BASE);
  if (!url.searchParams.has("idea")) url.searchParams.set("idea", idea);
  return `${url.pathname}${url.search}${url.hash}`;
}

/** Query string that preserves the handoff when linking between sign-in and sign-up. */
export function authQuery(params?: AuthSearchParams): string {
  const query = new URLSearchParams();
  const idea = readIdea(params);
  const next = toSafePath(firstValue(params?.next) ?? firstValue(params?.callbackUrl));

  if (idea) query.set("idea", idea);
  if (next && next !== "/") query.set("next", next);

  const serialised = query.toString();
  return serialised ? `?${serialised}` : "";
}
