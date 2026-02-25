import { Scale } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function PendingDecisions() {
  const decisions = useOpsStore((s) => s.decisions);
  const setDecisions = useOpsStore((s) => s.setDecisions);

  const handleResolve = async (decisionId: string, action: string) => {
    try {
      const res = await fetch(`${API_BASE}/ops/decisions/${decisionId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      if (res.ok) {
        setDecisions(decisions.filter((d) => d.id !== decisionId));
      }
    } catch {
      // ignore
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
        <Scale className="w-5 h-5" />
        Pending Decisions
        {decisions.length > 0 && (
          <span className="text-xs bg-[var(--color-warning)] text-white px-2 py-0.5 rounded-full">
            {decisions.length}
          </span>
        )}
      </h3>
      <div className="space-y-3">
        {decisions.length === 0 ? (
          <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-4 text-sm text-[var(--color-muted)] text-center">
            No pending decisions
          </div>
        ) : (
          decisions.map((d) => (
            <div
              key={d.id}
              className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-4 space-y-3"
            >
              <div>
                <div className="text-sm font-medium text-[var(--color-text)]">{d.title}</div>
                {d.description && (
                  <div className="text-xs text-[var(--color-muted)] mt-1">{d.description}</div>
                )}
                <div className="text-xs text-[var(--color-muted)] mt-1">
                  Requested by: {d.requestedBy}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleResolve(d.id, 'approve')}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--color-success)] text-white hover:opacity-90 transition-opacity"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleResolve(d.id, 'reject')}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--color-danger)] text-white hover:opacity-90 transition-opacity"
                >
                  Reject
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
