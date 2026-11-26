import type { ImgHTMLAttributes } from "react";

export function Avatar({ alt, className = "", ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  return (
    // Avatar images are user-provided and rendered at a fixed small size.
    <img
      alt={alt ?? ""}
      className={`size-10 rounded-full bg-grey-100 object-cover ${className}`}
      {...props}
    />
  );
}
