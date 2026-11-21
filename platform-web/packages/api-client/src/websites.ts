import { apiClient } from "./client";

export interface GenerateWebsiteResponse {
  site_id?: string;
  business_id: string;
  status: string;
  live_url?: string;
  pages?: string[];
}

export interface WebsiteStatusResponse {
  business_id: string;
  status: string;
  deployment_url: string | null;
  custom_domain: string | null;
  pages: { slug: string }[];
  attempt_count: number;
  last_attempt_at: string | null;
  last_error: string | null;
  updated_at: string;
}

export const websitesApi = {
  generateAndDeploy: (businessId: string) =>
    apiClient.request<GenerateWebsiteResponse>("/api/websites/generate-and-deploy", {
      method: "POST",
      body: JSON.stringify({ business_id: businessId }),
    }),

  retry: (businessId: string) =>
    apiClient.request<GenerateWebsiteResponse>(`/api/websites/${encodeURIComponent(businessId)}/retry`, {
      method: "POST",
    }),

  getStatus: (businessId: string) =>
    apiClient.request<WebsiteStatusResponse>(`/api/websites/${encodeURIComponent(businessId)}/status`),
};
