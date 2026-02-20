import { AlertTriangle, Info, ChevronDown } from 'lucide-react';
import { useState } from 'react';
import type { Warning } from '../../types';

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'var(--color-danger)',
  warning: 'var(--color-warning)',
  info: 'var(--color-primary)',
};

interface Props {
  warnings: Warning[];
}

export function WarningsPanel({ warnings }: Props) {
  const [expanded, setExpanded] = useState(false);
  if (warnings.length === 0) return null;

  const critical = warnings.filter((w) => w.severity === 'critical');
  const other = warnings.filter((w) => w.severity !== 'critical');

  return (
    <div className="space-y-2">
      {critical.map((w, i) => (
        <div
          key={`c-${i}`}
          className="p-3 rounded-lg border-l-4 bg-[var(--color-card)]"
          style={{ borderLeftColor: SEVERITY_COLORS.critical }}
        >
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-3.5 h-3.5 text-[var(--color-danger)]" />
            <span className="text-xs font-bold text-[var(--color-danger)] uppercase">CRITICAL</span>
            <span className="text-xs text-[var(--color-muted)]">{w.category}</span>
          </div>
          <div className="text-sm text-[var(--color-text)]">{w.message}</div>
          {w.suggestion && <div className="text-xs text-[var(--color-muted)] mt-1">{w.suggestion}</div>}
        </div>
      ))}

      {other.length > 0 && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-sm text-[var(--color-muted)] hover:text-[var(--color-text)] transition-colors"
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
            Warnings and insights ({other.length})
          </button>
          {expanded && (
            <div className="mt-2 space-y-2">
              {other.map((w, i) => {
                const color = SEVERITY_COLORS[w.severity] ?? SEVERITY_COLORS.info;
                const Icon = w.severity === 'warning' ? AlertTriangle : Info;
                return (
                  <div
                    key={`o-${i}`}
                    className="p-3 rounded-lg border-l-3 bg-[var(--color-card)]"
                    style={{ borderLeftColor: color, borderLeftWidth: '3px', borderLeftStyle: 'solid' }}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className="w-3.5 h-3.5" style={{ color }} />
                      <span className="text-xs font-bold uppercase" style={{ color }}>{w.severity}</span>
                      <span className="text-xs text-[var(--color-muted)]">{w.category}</span>
                    </div>
                    <div className="text-sm text-[var(--color-text)]">{w.message}</div>
                    {w.suggestion && <div className="text-xs text-[var(--color-muted)] mt-1">{w.suggestion}</div>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
