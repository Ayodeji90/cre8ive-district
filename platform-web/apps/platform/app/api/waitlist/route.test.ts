import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

const fetchMock = vi.fn(async () => new Response(null, { status: 204 }));

function request(payload: unknown) {
  return new Request("http://localhost/api/waitlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

describe("POST /api/waitlist", () => {
  beforeEach(() => {
    fetchMock.mockClear();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("normalizes and forwards a valid signup to the existing API", async () => {
    const response = await POST(
      request({
        email: "  Ada@Example.com ",
        source: "platform-home",
        business_description: "  A coffee shop in Lagos  ",
      }),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/waitlist",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          email: "ada@example.com",
          source: "platform-home",
          business_description: "A coffee shop in Lagos",
        }),
      }),
    );
  });

  it("rejects malformed email without calling the API", async () => {
    const response = await POST(request({ email: "not-an-email" }));

    expect(response.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("accepts the honeypot response without storing a signup", async () => {
    const response = await POST(request({ email: "bot@example.com", company: "spam" }));

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("reports an upstream failure instead of returning a success response", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 503 }));

    const response = await POST(request({ email: "ada@example.com" }));

    expect(response.status).toBe(502);
    expect(await response.json()).toEqual({
      error: "We couldn't add you to the list. Please try again.",
    });
  });
});
