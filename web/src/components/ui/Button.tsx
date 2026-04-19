import type { ButtonHTMLAttributes, ReactNode } from "react";
import { townSignFocus, townSignInteract } from "./townSign";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

type ButtonProps = {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
  fullWidth?: boolean;
} & ButtonHTMLAttributes<HTMLButtonElement>;

const variantClasses: Record<Variant, string> = {
  primary: [
    townSignInteract,
    "inline-flex items-center justify-center gap-2",
    "bg-accent",
    /* Tailwind `text-base` is font-size only — use explicit ink-on-accent (dark on cyan). */
    "text-[var(--color-base)]",
    "border-[color-mix(in_srgb,var(--color-accent),black_22%)]",
    "hover:bg-[color-mix(in_srgb,var(--color-accent),black_8%)]",
    townSignFocus,
  ].join(" "),
  secondary: [
    townSignInteract,
    "inline-flex items-center justify-center gap-2",
    "bg-surface text-ink",
    "border-[color-mix(in_srgb,var(--color-rule),black_14%)]",
    "hover:bg-surface2",
    townSignFocus,
  ].join(" "),
  ghost: [
    "inline-flex items-center justify-center gap-2",
    "rounded-[5px] border-2 border-dashed border-rule/55 bg-transparent text-ink2",
    "transition-[transform,background-color,border-color,color] duration-150 ease-out",
    "hover:border-rule hover:bg-surface2/70 hover:text-ink",
    "active:translate-y-px",
    townSignFocus,
  ].join(" "),
};

const sizeClasses: Record<Size, string> = {
  sm: "px-4 py-2.5 text-xs min-h-[44px] sm:min-h-0 sm:px-3 sm:py-1.5",
  md: "px-5 py-3.5 text-sm min-h-[48px] sm:min-h-0 sm:px-4 sm:py-2.5",
  lg: "px-6 py-4 text-sm min-h-[52px] sm:min-h-0 sm:px-6 sm:py-3 sm:text-base",
};

export const Button = ({
  variant = "primary",
  size = "md",
  children,
  fullWidth,
  className = "",
  type = "button",
  ...props
}: ButtonProps) => (
  <button
    type={type}
    className={[
      "cursor-pointer select-none font-mono font-semibold uppercase tracking-widest",
      "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-40",
      variantClasses[variant],
      sizeClasses[size],
      fullWidth ? "w-full" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ")}
    {...props}
  >
    {children}
  </button>
);
