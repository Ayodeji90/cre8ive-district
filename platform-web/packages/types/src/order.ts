export type PlanId = "starter" | "brand-web" | "complete";
export type OrderStatus = "pending" | "paid" | "failed" | "refunded";

export interface Plan {
  id: PlanId;
  name: string;
  amountNgn: number;
  description: string;
  features: string[];
}

export interface Order {
  id: string;
  businessId: string;
  planId: PlanId;
  amountNgn: number;
  status: OrderStatus;
  reference?: string;
  createdAt: string;
}
