import { Bell } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';

const URGENCY_COLORS = {
  low: 'bg-[var(--color-muted)]/20 text-[var(--color-muted)]',
  medium: 'bg-[var(--color-accent)]/20 text-[var(--color-accent)]',
  high: 'bg-[var(--color-warning)]/20 text-[var(--color-warning)]',
  critical: 'bg-[var(--color-danger)]/20 text-[var(--color-danger)]',
};

export function SignalInbox() {
  const signals = useOpsStore((s) => s.signals);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
        <Bell className="w-5 h-5" />
        Signal Inbox
        {signals.length > 0 && (
          <span className="text-xs bg-[var(--color-danger)] text-white px-2 py-0.5 rounded-full">
            {signals.length}
          </span>
        )}
      </h3>
      <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl max-h-80 overflow-y-auto">
        {signals.length === 0 ? (
          <div className="p-4 text-sm text-[var(--color-muted)] text-center">No signals</div>
        ) : (
          <div className="divide-y divide-[var(--color-border)]">
            {signals.map((signal) => (
              <div key={signal.id} className="px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${URGENCY_COLORS[signal.urgency]}`}>
                    {signal.urgency}
                  </span>
                  <span className="text-xs text-[var(--color-muted)]">{signal.source}</span>
                </div>
                <div className="text-sm text-[var(--color-text)]">{signal.message}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
