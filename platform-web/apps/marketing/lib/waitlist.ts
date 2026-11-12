export class WaitlistError extends Error {}

const API_URL = (
  process.env.API_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

export interface WaitlistSignup {
  email: string;
  source: string;
}

/**
 * Stores a waitlist signup in the backend API, which owns the database row and
 * sends the confirmation email.
 */
export async function addToWaitlist(signup: WaitlistSignup): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/waitlist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(signup),
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    throw new WaitlistError("Could not reach the waitlist service.");
  }

  if (!response.ok) {
    throw new WaitlistError(`Waitlist API returned ${response.status}.`);
  }
}
