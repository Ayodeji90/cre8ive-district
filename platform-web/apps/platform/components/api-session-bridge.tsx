"use client";

import { apiClient } from "@cre8ive/api-client";
import { getSession } from "next-auth/react";
import { useEffect } from "react";

export function ApiSessionBridge() {
  useEffect(() => {
    apiClient.setAccessTokenProvider(async () => (await getSession())?.accessToken ?? null);
    return () => apiClient.setAccessTokenProvider(undefined);
  }, []);

  return null;
}
