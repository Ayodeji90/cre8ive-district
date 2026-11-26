import { describe, expect, it } from "vitest";
import { getProductPage } from "./product-pages";

describe("product page content", () => {
  it("has public pages for the core platform capabilities", () => {
    expect(getProductPage("brand")?.title).toBe("Brand identity");
    expect(getProductPage("websites")?.title).toBe("Business websites");
    expect(getProductPage("approvals")?.title).toBe("Founder control");
  });

  it("labels future growth capabilities as in development", () => {
    expect(getProductPage("growth")?.status).toBe("In development");
    expect(getProductPage("growth")?.promise).toContain("not available features today");
  });

  it("does not resolve unknown product page slugs", () => {
    expect(getProductPage("pricing")).toBeUndefined();
  });
});
