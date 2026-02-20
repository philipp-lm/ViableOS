import { ShieldCheck, Eye, Siren, Ban } from 'lucide-react';
import type { Config } from '../../types';

interface Props {
  config: Config;
}

export function HitlSummary({ config }: Props) {
  const vs = config.viable_system;
  const hitl = vs.human_in_the_loop;
  const neverDo = vs.identity.never_do ?? [];
  const persistence = vs.persistence;

  if (!hitl && neverDo.length === 0) return null;

  return (
    <div className="space-y-6">
      {hitl && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Human-in-the-Loop</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="flex items-center gap-1.5 text-sm font-medium text-[var(--color-text)] mb-2">
                <ShieldCheck className="w-4 h-4 text-[var(--color-danger)]" /> Needs Your Approval
              </div>
              {hitl.approval_required?.map((item, i) => (
                <div key={i} className="text-xs text-[var(--color-muted)] py-0.5">- {item}</div>
              ))}
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-sm font-medium text-[var(--color-text)] mb-2">
                <Eye className="w-4 h-4 text-[var(--color-warning)]" /> Sent for Review
              </div>
              {hitl.review_required?.map((item, i) => (
                <div key={i} className="text-xs text-[var(--color-muted)] py-0.5">- {item}</div>
              ))}
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-sm font-medium text-[var(--color-text)] mb-2">
                <Siren className="w-4 h-4 text-[var(--color-danger)]" /> Emergency Alerts
              </div>
              {hitl.emergency_alerts?.map((item, i) => (
                <div key={i} className="text-xs text-[var(--color-muted)] py-0.5">- {item}</div>
              ))}
            </div>
          </div>
          {hitl.notification_channel && (
            <div className="text-xs text-[var(--color-muted)] mt-3">
              Notification channel: <span className="font-medium text-[var(--color-text)]">{hitl.notification_channel}</span>
            </div>
          )}
        </div>
      )}

      {neverDo.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Agent Boundaries (NEVER DO)</h3>
          <div className="space-y-1">
            {neverDo.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-red-300">
                <Ban className="w-3 h-3 text-[var(--color-danger)]" /> {item}
              </div>
            ))}
          </div>
        </div>
      )}

      {persistence?.strategy && persistence.strategy !== 'none' && (
        <div>
          <h3 className="text-lg font-semibold mb-2">State Persistence</h3>
          <div className="text-sm text-[var(--color-muted)]">
            Strategy: <span className="font-medium text-[var(--color-text)] capitalize">{persistence.strategy}</span>
            {persistence.path && <span className="ml-3">Path: <code className="text-[var(--color-muted)]">{persistence.path}</code></span>}
          </div>
        </div>
      )}
    </div>
  );
}
