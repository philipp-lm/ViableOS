import { Activity } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';

export function ActivityFeed() {
  const activity = useOpsStore((s) => s.activity);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
        <Activity className="w-5 h-5" />
        Activity Feed
      </h3>
      <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl max-h-80 overflow-y-auto">
        {activity.length === 0 ? (
          <div className="p-4 text-sm text-[var(--color-muted)] text-center">No recent activity</div>
        ) : (
          <div className="divide-y divide-[var(--color-border)]">
            {activity.map((item) => (
              <div key={item.id} className="px-4 py-3 flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-[var(--color-accent)] mt-1.5 shrink-0" />
                <div className="min-w-0">
                  <div className="text-sm text-[var(--color-text)]">{item.summary}</div>
                  <div className="text-xs text-[var(--color-muted)] mt-0.5 flex gap-2">
                    <span>{item.agent}</span>
                    <span>{item.type}</span>
                    {item.timestamp && <span>{new Date(item.timestamp).toLocaleTimeString()}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
