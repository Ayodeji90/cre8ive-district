import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Resend from "next-auth/providers/resend";
import { SignJWT, jwtVerify } from "jose";
import type { JWT, JWTDecodeParams, JWTEncodeParams } from "next-auth/jwt";
import type { AdapterUser } from "next-auth/adapters";
import { authAdapter } from "./auth-adapter";

const authSecret = process.env.JWT_SECRET ?? process.env.AUTH_SECRET ?? (
  process.env.NODE_ENV === "development" ? "dev-only-secret-change-me" : undefined
);
const maxAge = 30 * 24 * 60 * 60;

function signingKey() {
  if (!authSecret) throw new Error("Set JWT_SECRET or AUTH_SECRET before using authentication.");
  return new TextEncoder().encode(authSecret);
}

async function encodeApiToken({ token }: JWTEncodeParams): Promise<string> {
  if (!token) throw new Error("Cannot encode an empty session token.");
  const now = Math.floor(Date.now() / 1000);
  return new SignJWT({ ...token, iat: now, exp: now + maxAge, jti: token.jti ?? crypto.randomUUID() })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .sign(signingKey());
}

async function decodeApiToken({ token }: JWTDecodeParams): Promise<JWT | null> {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, signingKey(), { algorithms: ["HS256"] });
    return payload as JWT;
  } catch {
    return null;
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  // Stores users, linked OAuth accounts and magic-link tokens in the backend.
  adapter: authAdapter,
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID ?? process.env.AUTH_GOOGLE_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? process.env.AUTH_GOOGLE_SECRET ?? "",
    }),
    Resend({
      apiKey: process.env.RESEND_API_KEY ?? process.env.AUTH_RESEND_KEY ?? "",
      from:
        process.env.AUTH_EMAIL_FROM ??
        process.env.EMAIL_FROM ??
        "Cre8ive District <login@cre8ivedistrict.com>",
    }),
  ],
  // Keep issuing the backend-verifiable JWT even though an adapter is present;
  // NextAuth otherwise switches to database sessions.
  session: { strategy: "jwt", maxAge },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as AdapterUser & { role?: string }).role ?? "customer";
        token.picture = user.image ?? token.picture;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub ?? "";
        session.user.role = typeof token.role === "string" ? token.role : "customer";
      }
      session.accessToken = await encodeApiToken({ token, secret: authSecret ?? "", salt: "" });
      return session;
    },
  },
  pages: {
    signIn: "/sign-in",
    newUser: "/welcome",
  },
  secret: authSecret,
  trustHost: true,
  jwt: { maxAge, encode: encodeApiToken, decode: decodeApiToken },
});
