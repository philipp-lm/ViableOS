import { MessageSquare, Wand2, LayoutDashboard, Radio, RotateCcw } from 'lucide-react';
import { useConfigStore } from '../store/useConfigStore';
import { useChatStore } from '../store/useChatStore';
import { useOpsStore } from '../store/useOpsStore';

type View = 'chat' | 'wizard' | 'dashboard' | 'opsroom';

const NAV_ITEMS: { key: View; label: string; icon: typeof MessageSquare }[] = [
  { key: 'chat', label: 'Chat', icon: MessageSquare },
  { key: 'wizard', label: 'Wizard', icon: Wand2 },
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { key: 'opsroom', label: 'Ops Room', icon: Radio },
];

export function Sidebar() {
  const { view, setView, setWizardStep, resetConfig, config, wizardStep } = useConfigStore();
  const chatMessages = useChatStore((s) => s.messages);
  const opsConnected = useOpsStore((s) => s.connected);

  const getStatusDot = (key: View): string | null => {
    if (key === 'chat' && chatMessages.length > 0) return 'bg-[var(--color-accent)]';
    if (key === 'wizard' && config.viable_system.name) return 'bg-[var(--color-warning)]';
    if (key === 'dashboard' && config.viable_system.system_1.length > 0) return 'bg-[var(--color-success)]';
    if (key === 'opsroom' && opsConnected) return 'bg-[var(--color-success)]';
    return null;
  };

  return (
    <aside className="w-16 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg)] flex flex-col items-center py-4 gap-1 h-screen sticky top-0">
      <div className="text-xs font-bold text-[var(--color-primary)] mb-4 tracking-wider">
        V·OS
      </div>

      {NAV_ITEMS.map(({ key, label, icon: Icon }) => {
        const active = view === key;
        const dot = getStatusDot(key);
        return (
          <button
            key={key}
            onClick={() => setView(key)}
            className={`relative w-12 h-12 rounded-xl flex flex-col items-center justify-center gap-0.5 transition-all ${
              active
                ? 'bg-[var(--color-primary)]/15 text-[var(--color-primary)] border border-[var(--color-primary)]/30'
                : 'text-[var(--color-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-card)]'
            }`}
            title={label}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[9px] leading-none">{label}</span>
            {dot && (
              <span className={`absolute top-1.5 right-1.5 w-2 h-2 rounded-full ${dot}`} />
            )}
          </button>
        );
      })}

      <div className="mt-auto">
        <button
          onClick={() => {
            resetConfig();
            setView('wizard');
            setWizardStep(0);
          }}
          className="w-12 h-12 rounded-xl flex flex-col items-center justify-center gap-0.5 text-[var(--color-muted)] hover:text-[var(--color-danger)] hover:bg-[var(--color-card)] transition-all"
          title="Reset"
        >
          <RotateCcw className="w-4 h-4" />
          <span className="text-[9px] leading-none">Reset</span>
        </button>
      </div>
    </aside>
  );
}
