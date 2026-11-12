export type ReviewStatus = "pending" | "in_review" | "approved" | "revision_requested" | "rejected";

export interface Review {
  id: string;
  businessId: string;
  brandId: string;
  status: ReviewStatus;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}
