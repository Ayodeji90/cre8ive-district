export interface ApiClientOptions {
  baseUrl?: string;
  getAccessToken?: () => Promise<string | null>;
}

export interface ApiErrorShape {
  code?: string;
  message: string;
  status: number;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(error: ApiErrorShape) {
    super(error.message);
    this.name = "ApiError";
    this.status = error.status;
    this.code = error.code;
  }
}

export class ApiClient {
  private readonly baseUrl: string;
  private getAccessToken?: ApiClientOptions["getAccessToken"];

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
    this.getAccessToken = options.getAccessToken;
  }

  setAccessTokenProvider(provider?: ApiClientOptions["getAccessToken"]): void {
    this.getAccessToken = provider;
  }

  async request<TResponse>(path: string, init: RequestInit = {}): Promise<TResponse> {
    const token = await this.getAccessToken?.();
    const headers = new Headers(init.headers);
    headers.set("Accept", "application/json");
    if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const response = await fetch(`${this.baseUrl}${path}`, { ...init, headers });
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string; message?: string; code?: string } | null;
      throw new ApiError({
        status: response.status,
        code: payload?.code,
        message: payload?.detail ?? payload?.message ?? `Request failed (${response.status})`,
      });
    }
    if (response.status === 204) return undefined as TResponse;
    return (await response.json()) as TResponse;
  }
}

export const apiClient = new ApiClient();
