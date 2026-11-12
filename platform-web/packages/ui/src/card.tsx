import type { HTMLAttributes } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "elevated" | "interactive";
};

const variants = {
  default: "",
  elevated: "shadow-sm",
  interactive: "cursor-pointer transition-shadow hover:shadow-md",
} as const;

export function Card({ variant = "default", className = "", ...props }: CardProps) {
  return (
    <div
      className={`rounded-lg border border-grey-200 bg-white p-6 ${variants[variant]} ${className}`}
      {...props}
    />
  );
}

export function CardHeader({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`mb-4 space-y-1 ${className}`} {...props} />;
}

export function CardTitle({ className = "", ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={`text-xl font-semibold text-charcoal ${className}`} {...props} />;
}

export function CardDescription({ className = "", ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={`text-sm text-grey-600 ${className}`} {...props} />;
}
