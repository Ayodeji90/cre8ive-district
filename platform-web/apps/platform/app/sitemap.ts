import type { MetadataRoute } from "next";

const SITE_URL = "https://cre8ivedistrict.app";
const PUBLIC_PATHS = [
  "/",
  "/product/brand",
  "/product/websites",
  "/product/approvals",
  "/product/growth",
];

export default function sitemap(): MetadataRoute.Sitemap {
  return PUBLIC_PATHS.map((path) => ({
    url: new URL(path, SITE_URL).toString(),
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : 0.7,
  }));
}
