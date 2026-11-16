"use client";

interface AbijaAvatarProps {
  isThinking?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function AbijaAvatar({ isThinking = false, size = "md", className = "" }: AbijaAvatarProps) {
  const sizeClasses = {
    sm: "size-8",
    md: "size-10",
    lg: "size-12",
  }[size];

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${sizeClasses} ${className}`}>
      {/* Outer pulsing ring when thinking */}
      {isThinking && (
        <span
          className="absolute inset-0 rounded-full bg-orange/30 animate-ping duration-1000"
          aria-hidden="true"
        />
      )}

      {/* Main Avatar Circle */}
      <div className="relative flex items-center justify-center w-full h-full rounded-full bg-gradient-to-tr from-[#E05A2B] via-[#F36B35] to-[#F4B942] text-white shadow-sm ring-2 ring-white">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="size-1/2"
          aria-label="Abija AI Agent"
        >
          {/* Stylized African Crown / Spark Icon */}
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor" fillOpacity="0.2" />
          <path d="M12 2v20M2 12h20" strokeWidth="1.5" strokeDasharray="2 2" strokeOpacity="0.5" />
          <circle cx="12" cy="12" r="4" fill="currentColor" />
        </svg>

        {/* Live indicator pip */}
        <span
          className={`absolute -bottom-0.5 -right-0.5 size-2.5 rounded-full border-2 border-white ${
            isThinking ? "bg-amber-400 animate-pulse" : "bg-emerald-500"
          }`}
          title={isThinking ? "Abija is typing..." : "Abija is online"}
        />
      </div>
    </div>
  );
}
