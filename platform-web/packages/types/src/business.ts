/**
 * Wire shape of the Platform API `BusinessResponse` (snake_case, as serialised by the API).
 * This is the single definition used by `@cre8ive/api-client`; do not redeclare it there.
 */
export interface Business {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description: string | null;
  industry: string | null;
  location: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  plan: string;
  credit_balance: number;
  status: string;
  preferences: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface BusinessCreate {
  name: string;
  slug?: string;
  description?: string;
  industry?: string;
  location?: string;
  contact_phone?: string;
  contact_email?: string;
  preferences?: Record<string, unknown>;
}

export interface BusinessUpdate {
  name?: string;
  description?: string;
  industry?: string;
  location?: string;
  contact_phone?: string;
  contact_email?: string;
  preferences?: Record<string, unknown>;
}
