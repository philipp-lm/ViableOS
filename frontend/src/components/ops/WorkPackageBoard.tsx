import { Kanban } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';

const COLUMN_LABELS = {
  queued: 'Queued',
  active: 'Active',
  done: 'Done',
} as const;

const COLUMN_COLORS = {
  queued: 'border-[var(--color-muted)]',
  active: 'border-[var(--color-warning)]',
  done: 'border-[var(--color-success)]',
} as const;

export function WorkPackageBoard() {
  const workPackages = useOpsStore((s) => s.workPackages);

  const columns = {
    queued: workPackages.filter((w) => w.status === 'queued'),
    active: workPackages.filter((w) => w.status === 'active'),
    done: workPackages.filter((w) => w.status === 'done'),
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
        <Kanban className="w-5 h-5" />
        Work Packages
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {(Object.keys(COLUMN_LABELS) as Array<keyof typeof COLUMN_LABELS>).map((status) => (
          <div key={status} className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-[var(--color-muted)]">
              {COLUMN_LABELS[status]} ({columns[status].length})
            </div>
            <div className="space-y-2 min-h-[60px]">
              {columns[status].map((wp) => (
                <div
                  key={wp.id}
                  className={`bg-[var(--color-card)] border-l-2 ${COLUMN_COLORS[status]} border border-[var(--color-border)] rounded-lg p-2.5`}
                >
                  <div className="text-sm text-[var(--color-text)] font-medium truncate">{wp.title}</div>
                  {wp.assignee && (
                    <div className="text-xs text-[var(--color-muted)] mt-1">{wp.assignee}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
