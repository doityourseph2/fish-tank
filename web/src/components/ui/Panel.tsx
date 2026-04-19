import { useId, type ReactNode } from "react";

type PanelProps = {
  label?: string;
  /** Optional; if omitted, an id is generated for the panel heading. */
  labelId?: string;
  children: ReactNode;
  className?: string;
  accent?: boolean;
};

export const Panel = ({
  label,
  labelId: labelIdProp,
  children,
  className = "",
  accent,
}: PanelProps) => {
  const autoLabelId = useId();
  const labelId = label ? (labelIdProp ?? autoLabelId) : undefined;

  return (
    <section
      className={[
        "relative rounded-md border bg-surface",
        accent ? "border-accent/60" : "border-rule",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      aria-labelledby={label ? labelId : undefined}
    >
      {label ? (
        <div className="absolute -top-px left-3 -translate-y-1/2">
          <h2
            id={labelId}
            className="m-0 bg-surface px-2 py-0.5 text-sm font-semibold text-accent"
          >
            {label}
          </h2>
        </div>
      ) : null}
      {children}
    </section>
  );
};
