/**
 * Reference token map for consumers that still use Tailwind's legacy JS config.
 * Tailwind v4 apps import src/tokens.css instead; v4 does not load JS presets.
 */
export const tailwindPreset = {
  theme: {
    extend: {
      colors: {
        cream: "#f5f5ee",
        charcoal: "#2d2d2d",
        orange: { DEFAULT: "#f36b35", hover: "#e05e2a", light: "#fef3ee" },
        grey: { 100: "#f0f0ea", 200: "#e0e0d8", 400: "#a0a098", 600: "#606058" },
        success: "#2d8a4e",
        error: "#d94040",
        warning: "#e09b2d",
      },
      fontFamily: { sans: ['"Plus Jakarta Sans Variable"', '"Plus Jakarta Sans"', "system-ui", "sans-serif"] },
      maxWidth: { content: "72rem" },
      borderRadius: { sm: "0.375rem", md: "0.5rem", lg: "0.75rem", xl: "1rem" },
    },
  },
} as const;

export default tailwindPreset;
