import type { Order } from "@cre8ive/types";
import { apiClient } from "./client";

export interface BillingInitializeRequest {
  plan: string;
  business_id: string;
  email: string;
}

export interface BillingInitializeResponse {
  authorization_url: string;
  access_code: string;
  reference: string;
  amount: number;
  currency: string;
}

export interface BillingVerifyResponse {
  reference: string;
  status: string;
  order_id?: string | null;
}

export interface CreditBalanceResponse {
  business_id: string;
  balance: number;
}

export interface CreditTransaction {
  id: string;
  business_id: string;
  amount: number;
  balance_after: number;
  transaction_type: string;
  description: string;
  reference_id?: string | null;
  created_at: string;
}

export interface CreditLedgerResponse {
  business_id: string;
  balance: number;
  transactions: CreditTransaction[];
  total: number;
  page: number;
  limit: number;
}

export interface CreditDeductResponse {
  business_id: string;
  amount_deducted: number;
  new_balance: number;
  transaction_id: string;
}

export const billingApi = {
  initialize: (payload: BillingInitializeRequest) =>
    apiClient.request<BillingInitializeResponse>("/api/billing/initialize", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  verify: (reference: string) =>
    apiClient.request<BillingVerifyResponse>(`/api/billing/verify/${encodeURIComponent(reference)}`, {
      method: "POST",
    }),

  history: (businessId: string) =>
    apiClient.request<Order[]>(`/api/billing/${encodeURIComponent(businessId)}/history`),

  credits: (businessId: string) =>
    apiClient.request<CreditBalanceResponse>(`/api/billing/${encodeURIComponent(businessId)}/credits`),

  ledger: (businessId: string, page = 1, limit = 50) =>
    apiClient.request<CreditLedgerResponse>(
      `/api/billing/${encodeURIComponent(businessId)}/credits/ledger?page=${page}&limit=${limit}`
    ),

  deductCredits: (businessId: string, amount: number, description: string, referenceId?: string) =>
    apiClient.request<CreditDeductResponse>(
      `/api/billing/${encodeURIComponent(businessId)}/credits/deduct`,
      {
        method: "POST",
        body: JSON.stringify({ amount, description, reference_id: referenceId }),
      }
    ),

  topupCredits: (businessId: string, pack: "credits_50" | "credits_200" | "credits_500", email: string) =>
    apiClient.request<BillingInitializeResponse>("/api/billing/initialize", {
      method: "POST",
      body: JSON.stringify({ plan: pack, business_id: businessId, email }),
    }),
};
