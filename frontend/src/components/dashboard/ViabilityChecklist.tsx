import { CheckCircle, XCircle } from 'lucide-react';
import type { CheckResult } from '../../types';

interface Props {
  checks: CheckResult[];
}

export function ViabilityChecklist({ checks }: Props) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Viability Checklist</h3>
      <div className="grid grid-cols-3 gap-2">
        {checks.map((c) => (
          <div
            key={c.system}
            className="flex items-start gap-2.5 p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-card)]"
          >
            {c.present ? (
              <CheckCircle className="w-4 h-4 mt-0.5 text-[var(--color-success)] shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 mt-0.5 text-[var(--color-danger)] shrink-0" />
            )}
            <div>
              <div className="text-xs font-bold text-[var(--color-text)]">{c.system} {c.name}</div>
              <div className="text-xs text-[var(--color-muted)]">{c.details}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
