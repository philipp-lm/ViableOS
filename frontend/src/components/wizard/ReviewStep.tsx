import { StepHeader } from '../ui/StepHeader';
import { NavButtons } from '../ui/NavButtons';
import { useConfigStore } from '../../store/useConfigStore';
import { useViabilityCheck } from '../../hooks/useApiData';
import { CheckCircle, XCircle, AlertTriangle, Info, Rocket } from 'lucide-react';

const SEVERITY_STYLES = {
  critical: { color: 'var(--color-danger)', icon: AlertTriangle, label: 'CRITICAL' },
  warning: { color: 'var(--color-warning)', icon: AlertTriangle, label: 'WARNING' },
  info: { color: 'var(--color-primary)', icon: Info, label: 'INFO' },
};

export function ReviewStep() {
  const { config, setView, setWizardStep } = useConfigStore();
  const report = useViabilityCheck(config);
  const units = config.viable_system.system_1;

  if (!report) {
    return (
      <div>
        <StepHeader step={5} title="Review & Warnings" subtitle="Checking your configuration..." />
        <div className="text-center text-[var(--color-muted)] py-12">Analyzing...</div>
      </div>
    );
  }

  const hasBlockers = report.warnings.some((w) => w.severity === 'critical');

  return (
    <div>
      <StepHeader
        step={5}
        title="Review & Warnings"
        subtitle="Review your configuration before generating the OpenClaw package."
      />

      <div className="flex items-center gap-4 p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] mb-6">
        <div className="text-4xl font-bold text-[var(--color-text)]">
          {report.score}<span className="text-lg text-[var(--color-muted)]">/{report.total}</span>
        </div>
        <div>
          <div className="text-sm font-medium text-[var(--color-text)]">Viability Score</div>
          <div className="text-xs text-[var(--color-muted)]">
            {report.score === report.total ? 'Fully viable' : 'Some systems missing'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-6">
        {report.checks.map((c) => (
          <div
            key={c.system}
            className="flex items-start gap-2 p-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-card)]"
          >
            {c.present ? (
              <CheckCircle className="w-4 h-4 mt-0.5 text-[var(--color-success)] shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 mt-0.5 text-[var(--color-danger)] shrink-0" />
            )}
            <div>
              <div className="text-xs font-bold text-[var(--color-text)]">{c.system} {c.name}</div>
              <div className="text-xs text-[var(--color-muted)]">{c.details}</div>
            </div>
          </div>
        ))}
      </div>

      {report.warnings.length > 0 && (
        <div className="space-y-2 mb-6">
          <h3 className="text-sm font-semibold text-[var(--color-muted)] uppercase tracking-wider">Warnings</h3>
          {report.warnings.map((w, i) => {
            const style = SEVERITY_STYLES[w.severity] ?? SEVERITY_STYLES.info;
            const Icon = style.icon;
            return (
              <div
                key={i}
                className="p-3 rounded-lg border-l-4 bg-[var(--color-card)]"
                style={{ borderLeftColor: style.color }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="w-3.5 h-3.5" style={{ color: style.color }} />
                  <span className="text-xs font-bold uppercase" style={{ color: style.color }}>
                    {style.label}
                  </span>
                  <span className="text-xs text-[var(--color-muted)]">{w.category}</span>
                </div>
                <div className="text-sm text-[var(--color-text)]">{w.message}</div>
                {w.suggestion && (
                  <div className="text-xs text-[var(--color-muted)] mt-1">{w.suggestion}</div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="p-4 rounded-xl border bg-[var(--color-card)] mb-6"
        style={{ borderColor: units.length <= 2 ? 'var(--color-success)' : 'var(--color-warning)' }}>
        <div className="flex items-center gap-2 mb-1">
          <Rocket className="w-4 h-4" style={{ color: units.length <= 2 ? 'var(--color-success)' : 'var(--color-warning)' }} />
          <span className="text-sm font-medium text-[var(--color-text)]">Rollout recommendation</span>
        </div>
        <div className="text-xs text-[var(--color-muted)]">
          {units.length <= 2
            ? 'Good starting size. Launch all units and iterate.'
            : `You have ${units.length} units. Consider starting with 1-2 units, then adding more once they work end-to-end.`
          }
        </div>
      </div>

      <NavButtons
        onBack={() => setWizardStep(4)}
        onNext={() => setView('dashboard')}
        nextLabel={hasBlockers ? 'View Dashboard (with warnings)' : 'Go to Dashboard'}
      />
    </div>
  );
}
