import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import type { BudgetAllocation } from '../../types';

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#14b8a6', '#a855f7'];

interface Props {
  allocations: BudgetAllocation[];
  total: number;
}

export function BudgetChart({ allocations, total }: Props) {
  const data = allocations.map((a) => ({
    name: a.system,
    value: a.monthly_usd,
    pct: a.percentage,
  }));

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={65}
            outerRadius={100}
            dataKey="value"
            stroke="none"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null;
              const d = payload[0].payload;
              return (
                <div className="px-3 py-2 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] text-xs">
                  <div className="font-medium text-[var(--color-text)]">{d.name}</div>
                  <div className="text-[var(--color-muted)]">${d.value.toFixed(0)}/mo ({d.pct}%)</div>
                </div>
              );
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <div className="text-2xl font-bold text-[var(--color-text)]">${total.toFixed(0)}</div>
          <div className="text-xs text-[var(--color-muted)]">/ month</div>
        </div>
      </div>
    </div>
  );
}
