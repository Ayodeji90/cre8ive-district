import { apiClient } from "./client";

export interface Business {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description?: string | null;
  industry?: string | null;
  location?: string | null;
  contact_phone?: string | null;
  contact_email?: string | null;
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

export const businessesApi = {
  list: () => apiClient.request<Business[]>("/api/businesses"),
  get: (id: string) => apiClient.request<Business>(`/api/businesses/${encodeURIComponent(id)}`),
  create: (data: BusinessCreate) =>
    apiClient.request<Business>("/api/businesses", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: string, data: BusinessUpdate) =>
    apiClient.request<Business>(`/api/businesses/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};
