import { ImageResponse } from "next/og";

export const alt = "Cre8ive District — guided brand and website creation";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "76px 88px",
          background: "linear-gradient(135deg, #fffaf0 0%, #f2eee3 100%)",
          color: "#292822",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18, fontSize: 25, fontWeight: 700 }}>
          <div style={{ width: 48, height: 48, borderRadius: 16, background: "#f3a45b", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 30 }}>c</div>
          Cre8ive District
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ fontSize: 68, lineHeight: 1.05, fontWeight: 700, letterSpacing: -3, maxWidth: 940 }}>
            Shape your brand. Build your online presence.
          </div>
          <div style={{ fontSize: 28, color: "#69675e" }}>AI-assisted creative tools, with human review.</div>
        </div>
        <div style={{ fontSize: 20, color: "#8b5534", fontWeight: 700 }}>In development · Join the waitlist</div>
      </div>
    ),
    size,
  );
}
