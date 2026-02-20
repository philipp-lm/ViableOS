const TOTAL_STEPS = 6;

interface Props {
  step: number;
  title: string;
  subtitle?: string;
}

export function StepHeader({ step, title, subtitle }: Props) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-1">
        <span className="text-xs font-bold text-[var(--color-muted)] uppercase tracking-wider">
          Step {step + 1} of {TOTAL_STEPS}
        </span>
        <div className="flex-1 h-1 rounded-full bg-[var(--color-border)]">
          <div
            className="h-1 rounded-full bg-[var(--color-primary)] transition-all duration-500"
            style={{ width: `${((step + 1) / TOTAL_STEPS) * 100}%` }}
          />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-[var(--color-text)] mt-3">{title}</h2>
      {subtitle && (
        <p className="text-sm text-[var(--color-muted)] mt-1">{subtitle}</p>
      )}
    </div>
  );
}
