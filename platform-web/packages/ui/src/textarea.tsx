import type { TextareaHTMLAttributes } from "react";

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export function Textarea({ label, hint, error, id, className = "", ...props }: TextareaProps) {
  const textareaId = id ?? props.name;
  return (
    <div className="grid gap-1.5">
      {label && (
        <label htmlFor={textareaId} className="text-sm font-medium text-charcoal">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${textareaId}-error` : hint ? `${textareaId}-hint` : undefined}
        className={`min-h-28 w-full resize-y rounded-sm border bg-white px-3 py-2.5 text-sm text-charcoal placeholder:text-grey-400 focus:border-orange focus:ring-2 focus:ring-orange/30 focus:outline-none ${error ? "border-error" : "border-grey-200"} ${className}`}
        {...props}
      />
      {hint && !error && <p id={`${textareaId}-hint`} className="text-xs text-grey-600">{hint}</p>}
      {error && <p id={`${textareaId}-error`} role="alert" className="text-xs text-error">{error}</p>}
    </div>
  );
}
