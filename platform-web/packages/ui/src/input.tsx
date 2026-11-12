import type { InputHTMLAttributes, ReactNode } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  leading?: ReactNode;
}

export function Input({ label, hint, error, leading, id, className = "", ...props }: InputProps) {
  const inputId = id ?? props.name;
  return (
    <div className="grid gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-charcoal">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {leading && <span className="absolute left-3 text-grey-600">{leading}</span>}
        <input
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          className={`h-10 w-full rounded-sm border bg-white px-3 text-sm text-charcoal placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/30 focus:outline-none ${leading ? "pl-9" : ""} ${error ? "border-error" : "border-grey-200"} ${className}`}
          {...props}
        />
      </div>
      {hint && !error && <p id={`${inputId}-hint`} className="text-xs text-grey-600">{hint}</p>}
      {error && <p id={`${inputId}-error`} role="alert" className="text-xs text-error">{error}</p>}
    </div>
  );
}
