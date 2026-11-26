import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WaitlistForm } from "./waitlist-form";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("WaitlistForm", () => {
  it("submits the signup and offers an idea-preserving workspace handoff", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<WaitlistForm />);

    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "Ada@Example.com" },
    });
    fireEvent.change(screen.getByLabelText(/What are you building/), {
      target: { value: "A coffee shop in Lagos" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Join the waitlist/ }));

    await screen.findByRole("status");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/waitlist",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          email: "ada@example.com",
          source: "platform-home",
          business_description: "A coffee shop in Lagos",
          company: "",
        }),
      }),
    );
    expect(screen.getByRole("link", { name: /Start your workspace with this idea/ }).getAttribute("href")).toBe(
      "/sign-up?next=%2Fworkspace&idea=A+coffee+shop+in+Lagos",
    );
  });

  it("shows a clear error when the waitlist request fails", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: "Waitlist is temporarily unavailable." }), { status: 502 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<WaitlistForm />);

    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "ada@example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Join the waitlist/ }));

    await waitFor(() => {
      expect(screen.getByRole("alert").textContent).toBe("Waitlist is temporarily unavailable.");
    });
  });
});
