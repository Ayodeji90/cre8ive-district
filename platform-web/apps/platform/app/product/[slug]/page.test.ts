import { describe, expect, it } from "vitest";
import { generateMetadata } from "./page";

describe("product page metadata", () => {
  it("uses a single branded title and a slug-specific canonical URL", async () => {
    const metadata = await generateMetadata({
      params: Promise.resolve({ slug: "brand" }),
    });

    expect(metadata.title).toBe("Brand identity");
    expect(metadata.alternates?.canonical).toBe("/product/brand");
  });
});
