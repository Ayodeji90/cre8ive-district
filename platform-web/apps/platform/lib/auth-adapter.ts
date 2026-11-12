import type { Adapter, AdapterUser, VerificationToken } from "next-auth/adapters";

/**
 * NextAuth adapter backed by the FastAPI service.
 *
 * NextAuth needs somewhere to store users, linked OAuth accounts and
 * single-use magic-link tokens. Rather than adding a second database to the
 * Next.js app, this adapter calls the backend's internal adapter routes, which
 * write to the same Postgres `users` table the API already uses.
 */

const API_URL = (
  process.env.API_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

const ADAPTER_SECRET =
  process.env.AUTH_ADAPTER_SECRET ??
  process.env.JWT_SECRET ??
  process.env.AUTH_SECRET ??
  "";

type ApiUser = {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  role?: string;
  emailVerified: string | null;
};

type ApiVerificationToken = {
  identifier: string;
  token: string;
  expires: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api/auth/adapter${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Auth-Adapter-Secret": ADAPTER_SECRET,
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (response.status === 404) return null as T;
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `Auth adapter request failed (${response.status} ${path})${detail ? `: ${detail}` : ""}`,
    );
  }
  if (response.status === 204) return null as T;
  return (await response.json()) as T;
}

function toAdapterUser(user: ApiUser): AdapterUser {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    image: user.image,
    emailVerified: user.emailVerified ? new Date(user.emailVerified) : null,
    role: user.role,
  } as AdapterUser;
}

function toApiUser(user: Partial<AdapterUser>) {
  return {
    ...(user.name !== undefined ? { name: user.name } : {}),
    ...(user.email !== undefined ? { email: user.email } : {}),
    ...(user.image !== undefined ? { image: user.image } : {}),
    ...(user.emailVerified !== undefined
      ? { emailVerified: user.emailVerified?.toISOString() ?? null }
      : {}),
  };
}

export const authAdapter: Adapter = {
  async createUser(user) {
    const created = await request<ApiUser>("/users", {
      method: "POST",
      body: JSON.stringify(toApiUser(user)),
    });
    return toAdapterUser(created);
  },

  async getUser(id) {
    const user = await request<ApiUser | null>(`/users/${encodeURIComponent(id)}`);
    return user ? toAdapterUser(user) : null;
  },

  async getUserByEmail(email) {
    const user = await request<ApiUser | null>(
      `/users/lookup?email=${encodeURIComponent(email)}`,
    );
    return user ? toAdapterUser(user) : null;
  },

  async getUserByAccount({ provider, providerAccountId }) {
    const account = await request<{ user_id: string } | null>(
      `/accounts?provider=${encodeURIComponent(provider)}&provider_account_id=${encodeURIComponent(providerAccountId)}`,
    );
    if (!account) return null;
    const user = await request<ApiUser | null>(
      `/users/${encodeURIComponent(account.user_id)}`,
    );
    return user ? toAdapterUser(user) : null;
  },

  async updateUser(user) {
    const updated = await request<ApiUser>(
      `/users/${encodeURIComponent(user.id)}`,
      {
        method: "PATCH",
        body: JSON.stringify(toApiUser(user)),
      },
    );
    return toAdapterUser(updated);
  },

  async deleteUser(userId) {
    await request(`/users/${encodeURIComponent(userId)}`, { method: "DELETE" });
  },

  async linkAccount(account) {
    await request("/accounts", {
      method: "POST",
      body: JSON.stringify({
        user_id: account.userId,
        type: account.type,
        provider: account.provider,
        provider_account_id: account.providerAccountId,
        refresh_token: account.refresh_token ?? null,
        access_token: account.access_token ?? null,
        expires_at: account.expires_at ?? null,
        token_type: account.token_type ?? null,
        scope: account.scope ?? null,
        id_token: account.id_token ?? null,
        session_state:
          typeof account.session_state === "string"
            ? account.session_state
            : account.session_state
              ? JSON.stringify(account.session_state)
              : null,
      }),
    });
  },

  async createVerificationToken(token: VerificationToken) {
    const created = await request<ApiVerificationToken>("/verification-tokens", {
      method: "POST",
      body: JSON.stringify({
        identifier: token.identifier,
        token: token.token,
        expires: token.expires.toISOString(),
      }),
    });
    return {
      identifier: created.identifier,
      token: created.token,
      expires: new Date(created.expires),
    };
  },

  async useVerificationToken({ identifier, token }) {
    const used = await request<ApiVerificationToken | null>(
      "/verification-tokens/consume",
      {
        method: "POST",
        body: JSON.stringify({ identifier, token }),
      },
    );
    if (!used) return null;
    return {
      identifier: used.identifier,
      token: used.token,
      expires: new Date(used.expires),
    };
  },
};
