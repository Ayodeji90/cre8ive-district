import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@cre8ive/api-client", "@cre8ive/tokens", "@cre8ive/types", "@cre8ive/ui"],
  experimental: { cpus: 2 },
};

export default nextConfig;
