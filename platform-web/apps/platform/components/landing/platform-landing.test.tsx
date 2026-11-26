import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformLanding } from "./platform-landing";

describe("PlatformLanding", () => {
  it("preserves the entered idea through sign-up and sign-in handoffs", () => {
    render(<PlatformLanding />);

    fireEvent.click(screen.getByRole("button", { name: "Talk to Abija" }));
    fireEvent.change(screen.getByLabelText("What would you like to build?"), {
      target: { value: "A coffee shop in Lagos" },
    });

    expect(screen.getByRole("link", { name: /Send to Abija/ }).getAttribute("href")).toBe(
      "/sign-up?next=%2Fworkspace&idea=A+coffee+shop+in+Lagos",
    );
    expect(screen.getByRole("link", { name: /Already have an account/ }).getAttribute("href")).toBe(
      "/sign-in?next=%2Fworkspace&idea=A+coffee+shop+in+Lagos",
    );
  });

  it("opens the Abija tab and prefills ideas carried on the homepage URL", () => {
    render(<PlatformLanding initialIdea="A natural skincare brand" />);

    expect(screen.getByRole("button", { name: "Talk to Abija" }).getAttribute("aria-pressed")).toBe("true");
    expect((screen.getByLabelText("What would you like to build?") as HTMLTextAreaElement).value).toBe(
      "A natural skincare brand",
    );
  });

  it("opens the idea tab when arriving from a product page", () => {
    render(<PlatformLanding startWithIdea />);

    expect(screen.getByRole("button", { name: "Talk to Abija" }).getAttribute("aria-pressed")).toBe("true");
  });

  it("shows a primary submit action only after the visitor enters an idea", () => {
    render(<PlatformLanding />);

    expect(screen.getByRole("button", { name: "Add your idea to begin" }).hasAttribute("disabled")).toBe(true);
    fireEvent.change(screen.getByLabelText("What would you like to build?"), {
      target: { value: "A local food marketplace" },
    });

    expect(screen.getByRole("link", { name: /Send to Abija/ }).getAttribute("href")).toContain(
      "idea=A+local+food+marketplace",
    );
  });

  it("updates the workflow preview when a step is selected", () => {
    render(<PlatformLanding />);

    fireEvent.click(screen.getByRole("button", { name: /Shape your brand/ }));

    expect(screen.getByRole("heading", { name: "Shape your brand" }).textContent).toBe("Shape your brand");
    expect(screen.getByText("Brand direction").textContent).toBe("Brand direction");
  });
});
