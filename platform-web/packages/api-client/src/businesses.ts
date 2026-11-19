import type { Business, BusinessCreate, BusinessUpdate } from "@cre8ive/types";
import { apiClient } from "./client";

export type { Business, BusinessCreate, BusinessUpdate };

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
