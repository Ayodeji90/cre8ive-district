import type { Brand } from "@cre8ive/types";
import { apiClient } from "./client";

export const brandsApi = {
  get: (id: string) => apiClient.request<Brand>(`/api/brands/${encodeURIComponent(id)}`),
  preview: <TPreview = unknown>(id: string) => apiClient.request<TPreview>(`/api/brands/${encodeURIComponent(id)}/preview`),
};
