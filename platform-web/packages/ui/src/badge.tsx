import type { HTMLAttributes } from "react";

const tones = {
  neutral: "bg-grey-100 text-grey-600",
  orange: "bg-orange-light text-orange-hover",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-charcoal",
  error: "bg-error/10 text-error",
} as const;

export function Badge({ tone = "neutral", className = "", ...props }: HTMLAttributes<HTMLSpanElement> & { tone?: keyof typeof tones }) {
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${tones[tone]} ${className}`} {...props} />;
}
