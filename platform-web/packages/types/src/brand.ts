export interface ColorPalette {
  name: string;
  hex: string;
  role?: string;
}

export interface FontPair {
  heading: string;
  body: string;
}

export interface BrandStrategy {
  positioning: string;
  audience: string;
  personality: string[];
  differentiator: string;
}

export type BrandStatus = "draft" | "generating" | "in_review" | "approved" | "published";

export interface Brand {
  id: string;
  businessId: string;
  name: string;
  tagline?: string;
  story?: string;
  status: BrandStatus;
  palette: ColorPalette[];
  fonts: FontPair;
  strategy?: BrandStrategy;
  logoUrls: string[];
  createdAt: string;
  updatedAt: string;
}
