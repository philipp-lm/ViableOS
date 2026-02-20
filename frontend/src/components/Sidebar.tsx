import { RotateCcw } from 'lucide-react';
import { useTemplates } from '../hooks/useApiData';
import { useConfigStore } from '../store/useConfigStore';

export function Sidebar() {
  const templates = useTemplates();
  const { loadTemplate, resetConfig, setWizardStep, setView } = useConfigStore();

  const handleDemo = async (key: string) => {
    if (key === 'custom') return;
    await loadTemplate(key);
    setView('dashboard');
  };

  return (
    <aside className="w-52 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg)] p-4 flex flex-col gap-2 overflow-y-auto h-screen sticky top-0">
      <div className="mb-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[var(--color-muted)]">
          Quick demos
        </div>
        <div className="text-xs text-[var(--color-muted)] mt-1">
          Load a fully configured system instantly.
        </div>
      </div>

      {templates
        .filter((t) => t.key !== 'custom')
        .map((t) => (
          <button
            key={t.key}
            onClick={() => handleDemo(t.key)}
            className="text-left px-3 py-2 rounded-lg text-sm border border-[var(--color-border)] bg-transparent text-[var(--color-muted)] hover:border-[var(--color-primary)] hover:text-[var(--color-text)] transition-all"
          >
            {t.name}
          </button>
        ))}

      <div className="mt-auto pt-4">
        <button
          onClick={() => {
            resetConfig();
            setView('wizard');
            setWizardStep(0);
          }}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs text-[var(--color-muted)] border border-[var(--color-border)] hover:border-[var(--color-danger)] hover:text-[var(--color-danger)] transition-all"
        >
          <RotateCcw className="w-3 h-3" />
          Reset everything
        </button>
      </div>
    </aside>
  );
}
