import type { Order } from "@cre8ive/types";
import { apiClient } from "./client";

export interface BillingInitializeResponse {
  authorization_url: string;
  reference: string;
}

export const billingApi = {
  initialize: (planId: string, businessId: string) => apiClient.request<BillingInitializeResponse>("/api/billing/initialize", {
    method: "POST",
    body: JSON.stringify({ plan_id: planId, business_id: businessId }),
  }),
  verify: (reference: string) => apiClient.request<{ status: string; order: Order }>(`/api/billing/verify/${encodeURIComponent(reference)}`, { method: "POST" }),
};
