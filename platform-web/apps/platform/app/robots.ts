import type { MetadataRoute } from "next";

const SITE_URL = "https://cre8ivedistrict.app";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/workspace", "/api/"],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
