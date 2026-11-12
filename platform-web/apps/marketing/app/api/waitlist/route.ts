import { NextResponse } from "next/server";
import { addToWaitlist, WaitlistError } from "../../../lib/waitlist";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validationError(message: string) {
  return NextResponse.json({ error: message }, { status: 400 });
}

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return validationError("Send a JSON body with an email address.");
  }

  if (typeof payload !== "object" || payload === null) {
    return validationError("Send a JSON body with an email address.");
  }

  const { email, source, company } = payload as Record<string, unknown>;

  // Honeypot: real visitors never see this field. Pretend it worked so bots
  // do not learn anything from the response.
  if (typeof company === "string" && company.trim() !== "") {
    return NextResponse.json({ ok: true });
  }

  if (typeof email !== "string") return validationError("Enter an email address.");

  const normalizedEmail = email.trim().toLowerCase();
  if (normalizedEmail.length > 254 || !EMAIL_PATTERN.test(normalizedEmail)) {
    return validationError("Enter a valid email address.");
  }

  const normalizedSource =
    typeof source === "string" && /^[a-z0-9-]{1,32}$/.test(source) ? source : "unknown";

  try {
    await addToWaitlist({ email: normalizedEmail, source: normalizedSource });
    return NextResponse.json({ ok: true });
  } catch (error) {
    if (!(error instanceof WaitlistError)) {
      console.error("Unexpected waitlist error", error);
    }
    return NextResponse.json(
      { error: "We couldn't add you to the list. Please try again." },
      { status: 502 },
    );
  }
}
