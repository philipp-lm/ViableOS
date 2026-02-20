import type { BudgetPlan, ViabilityReport } from '../../types';

interface Props {
  plan: BudgetPlan;
  report: ViabilityReport;
}

export function MetricsBar({ plan, report }: Props) {
  const critical = report.warnings.filter((w) => w.severity === 'critical').length;
  const warning = report.warnings.filter((w) => w.severity === 'warning').length;

  const metrics = [
    { label: 'Viability Score', value: `${report.score}/${report.total}` },
    { label: 'Monthly Budget', value: `$${plan.total_monthly_usd.toFixed(0)}` },
    { label: 'Strategy', value: plan.strategy.charAt(0).toUpperCase() + plan.strategy.slice(1) },
    { label: 'Agents', value: String(plan.allocations.length) },
    { label: 'Warnings', value: `${critical}C / ${warning}W` },
  ];

  return (
    <div className="grid grid-cols-5 gap-3">
      {metrics.map((m) => (
        <div
          key={m.label}
          className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] text-center"
        >
          <div className="text-xl font-bold text-[var(--color-text)]">{m.value}</div>
          <div className="text-xs text-[var(--color-muted)] mt-1">{m.label}</div>
        </div>
      ))}
    </div>
  );
}
