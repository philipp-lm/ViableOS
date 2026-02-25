import { Bot } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';
import type { AgentStatus } from '../../types';

const STATUS_COLORS: Record<AgentStatus, string> = {
  online: 'bg-[var(--color-success)]',
  working: 'bg-[var(--color-warning)]',
  error: 'bg-[var(--color-danger)]',
  offline: 'bg-[var(--color-muted)]',
};

const STATUS_LABELS: Record<AgentStatus, string> = {
  online: 'Online',
  working: 'Working',
  error: 'Error',
  offline: 'Offline',
};

export function AgentStatusGrid() {
  const agents = useOpsStore((s) => s.agents);

  if (agents.length === 0) {
    return (
      <div className="text-sm text-[var(--color-muted)] text-center py-4">
        No agents found.
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">Agent Status</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-3 space-y-2"
          >
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-[var(--color-muted)]" />
              <span className="text-sm font-medium text-[var(--color-text)] truncate">{agent.name}</span>
              <span className={`ml-auto w-2.5 h-2.5 rounded-full shrink-0 ${STATUS_COLORS[agent.status]}`} />
            </div>
            <div className="text-xs text-[var(--color-muted)]">{agent.role}</div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-[var(--color-muted)]">
                {STATUS_LABELS[agent.status]}
              </span>
            </div>
            {agent.currentTask && (
              <div className="text-xs text-[var(--color-accent)] truncate">
                {agent.currentTask}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
