import type { Business, Review } from "@cre8ive/types";
import { apiClient } from "./client";

export const adminApi = {
  reviews: (status = "pending") => apiClient.request<Review[]>(`/api/admin/reviews?status=${encodeURIComponent(status)}`),
  review: (id: string) => apiClient.request<Review>(`/api/admin/reviews/${encodeURIComponent(id)}`),
  businesses: () => apiClient.request<Business[]>("/api/admin/businesses"),
  business: (id: string) => apiClient.request<Business>(`/api/admin/businesses/${encodeURIComponent(id)}`),
};
