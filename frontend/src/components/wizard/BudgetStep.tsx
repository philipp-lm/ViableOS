import { StepHeader } from '../ui/StepHeader';
import { NavButtons } from '../ui/NavButtons';
import { InfoCallout } from '../ui/InfoCallout';
import { useConfigStore } from '../../store/useConfigStore';
import { useModels, useBudget } from '../../hooks/useApiData';
import { AlertTriangle, ChevronDown } from 'lucide-react';
import { useEffect, useState } from 'react';

const PROVIDERS = [
  { key: 'anthropic', label: 'Anthropic (Claude)' },
  { key: 'openai', label: 'OpenAI (GPT)' },
  { key: 'google', label: 'Google (Gemini)' },
  { key: 'deepseek', label: 'DeepSeek' },
  { key: 'xai', label: 'xAI (Grok)' },
  { key: 'meta', label: 'Meta (Llama)' },
  { key: 'ollama', label: 'Ollama (Local)' },
  { key: 'mixed', label: 'Mixed (best of each)' },
];

const STRATEGIES = [
  { key: 'frugal', label: 'Frugal', desc: 'Minimize cost, budget models' },
  { key: 'balanced', label: 'Balanced', desc: 'Good quality, moderate cost' },
  { key: 'performance', label: 'Performance', desc: 'Best models, highest cost' },
];

const ROUTING_KEYS = [
  { key: 's2_coordination', label: 'S2 Coordinator' },
  { key: 's3_optimization', label: 'S3 Optimizer' },
  { key: 's3_star_audit', label: 'S3* Auditor' },
  { key: 's4_intelligence', label: 'S4 Scout' },
  { key: 's5_preparation', label: 'S5 Guardian' },
];

export function BudgetStep() {
  const { config, updateVs, setWizardStep } = useConfigStore();
  const models = useModels();
  const plan = useBudget(config);
  const vs = config.viable_system;
  const DEFAULT_ALERTS = { warn_at_percent: 80, auto_downgrade_at_percent: 95 };
  const budget = vs.budget ?? { monthly_usd: 150, strategy: 'balanced', alerts: DEFAULT_ALERTS };
  const routing = vs.model_routing ?? {};
  const [showSystemModels, setShowSystemModels] = useState(false);

  useEffect(() => {
    if (!vs.budget?.alerts) {
      updateVs({ budget: { ...budget, alerts: DEFAULT_ALERTS } });
    }
  }, []);

  const updateBudget = (partial: Record<string, unknown>) => {
    updateVs({ budget: { ...budget, ...partial } as typeof budget });
  };

  const updateRouting = (key: string, value: string) => {
    updateVs({ model_routing: { ...routing, [key]: value } });
  };

  const modelSelect = (value: string, onChange: (v: string) => void, label: string) => {
    const selected = models.find((m) => m.id === value);
    return (
      <div>
        <label className="block text-xs text-[var(--color-muted)] mb-1">{label}</label>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
        >
          <option value="">Default</option>
          {models.map((m) => (
            <option key={m.id} value={m.id}>
              {m.id} ({m.tier}, {m.agent_reliability})
            </option>
          ))}
        </select>
        {selected?.warning && (
          <div className="flex items-start gap-1.5 mt-1 text-xs text-[var(--color-warning)]">
            <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
            {selected.warning}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <StepHeader
        step={3}
        title="Budget & AI Models"
        subtitle="Set your monthly token budget and choose AI models for each system."
      />

      <InfoCallout title="Community insight: Token costs">
        Token costs are the #1 issue. Setting a budget with the right strategy prevents cost spirals.
        Start frugal, upgrade when you see what works.
      </InfoCallout>

      <div className="space-y-6 mt-6">
        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">
            Monthly budget: <span className="text-[var(--color-text)] font-bold">${budget.monthly_usd}</span>
          </label>
          <input
            type="range"
            min={10}
            max={1000}
            step={10}
            value={budget.monthly_usd}
            onChange={(e) => updateBudget({ monthly_usd: Number(e.target.value) })}
            className="w-full accent-[var(--color-primary)]"
          />
          <div className="flex justify-between text-xs text-[var(--color-muted)]">
            <span>$10</span><span>$1,000</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">Strategy</label>
          <div className="grid grid-cols-3 gap-2">
            {STRATEGIES.map((s) => (
              <button
                key={s.key}
                onClick={() => updateBudget({ strategy: s.key })}
                className={`p-3 rounded-lg border text-left transition-all ${
                  budget.strategy === s.key
                    ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
                    : 'border-[var(--color-border)] bg-[var(--color-card)] hover:border-[var(--color-primary)]'
                }`}
              >
                <div className="text-sm font-medium text-[var(--color-text)]">{s.label}</div>
                <div className="text-xs text-[var(--color-muted)] mt-0.5">{s.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">Default provider</label>
          <select
            value={routing.provider_preference ?? 'anthropic'}
            onChange={(e) => updateRouting('provider_preference', e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
          >
            {PROVIDERS.map((p) => (
              <option key={p.key} value={p.key}>{p.label}</option>
            ))}
          </select>
        </div>

        {vs.system_1.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">
              Per-unit model & weight
            </label>
            <div className="space-y-3">
              {vs.system_1.map((unit, i) => (
                <div key={i} className="p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-card)]">
                  <div className="text-sm font-medium text-[var(--color-text)] mb-2">{unit.name || `Unit ${i + 1}`}</div>
                  <div className="grid grid-cols-2 gap-3">
                    {modelSelect(unit.model ?? '', (v) => {
                      const next = [...vs.system_1];
                      next[i] = { ...unit, model: v || undefined };
                      updateVs({ system_1: next });
                    }, 'Model')}
                    <div>
                      <label className="block text-xs text-[var(--color-muted)] mb-1">
                        Weight: {unit.weight ?? 5}
                      </label>
                      <input
                        type="range"
                        min={1}
                        max={10}
                        value={unit.weight ?? 5}
                        onChange={(e) => {
                          const next = [...vs.system_1];
                          next[i] = { ...unit, weight: Number(e.target.value) };
                          updateVs({ system_1: next });
                        }}
                        className="w-full accent-[var(--color-primary)]"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <button
            onClick={() => setShowSystemModels(!showSystemModels)}
            className="flex items-center gap-2 text-sm text-[var(--color-muted)] hover:text-[var(--color-text)] transition-colors"
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${showSystemModels ? 'rotate-180' : ''}`} />
            Per-system model overrides (S2-S5)
          </button>
          {showSystemModels && (
            <div className="mt-3 space-y-3 p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-card)]">
              {ROUTING_KEYS.map(({ key, label }) =>
                modelSelect(routing[key] ?? '', (v) => updateRouting(key, v), label)
              )}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">Budget alerts</label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-[var(--color-muted)] mb-1">Warn at %</label>
              <input
                type="number"
                min={50}
                max={100}
                value={budget.alerts?.warn_at_percent ?? 80}
                onChange={(e) => updateBudget({ alerts: { ...budget.alerts, warn_at_percent: Number(e.target.value) } })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--color-muted)] mb-1">Auto-downgrade at %</label>
              <input
                type="number"
                min={50}
                max={100}
                value={budget.alerts?.auto_downgrade_at_percent ?? 95}
                onChange={(e) => updateBudget({ alerts: { ...budget.alerts, auto_downgrade_at_percent: Number(e.target.value) } })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>

        {plan && (
          <div className="p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-card)]">
            <div className="text-sm font-medium text-[var(--color-muted)] mb-2">Budget preview</div>
            <div className="space-y-1">
              {plan.allocations.map((a) => (
                <div key={a.system} className="flex justify-between text-xs">
                  <span className="text-[var(--color-muted)]">{a.friendly_name}</span>
                  <span className="text-[var(--color-text)] font-mono">${a.monthly_usd.toFixed(0)} ({a.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <NavButtons onBack={() => setWizardStep(2)} onNext={() => setWizardStep(4)} />
    </div>
  );
}
