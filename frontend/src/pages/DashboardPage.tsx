import { useConfigStore } from '../store/useConfigStore';
import { useBudget, useViabilityCheck } from '../hooks/useApiData';
import { MetricsBar } from '../components/dashboard/MetricsBar';
import { WarningsPanel } from '../components/dashboard/WarningsPanel';
import { VsmDiagram } from '../components/dashboard/VsmDiagram';
import { BudgetChart } from '../components/dashboard/BudgetChart';
import { ModelRouting } from '../components/dashboard/ModelRouting';
import { ViabilityChecklist } from '../components/dashboard/ViabilityChecklist';
import { AgentCards } from '../components/dashboard/AgentCards';
import { HitlSummary } from '../components/dashboard/HitlSummary';
import { ExportPanel } from '../components/dashboard/ExportPanel';
import { Pencil } from 'lucide-react';

export function DashboardPage() {
  const { config, setView, setWizardStep } = useConfigStore();
  const vs = config.viable_system;
  const plan = useBudget(config);
  const report = useViabilityCheck(config);

  if (!vs.name) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
        <p className="text-[var(--color-muted)]">No configuration loaded. Run the wizard first.</p>
        <button
          onClick={() => { setView('wizard'); setWizardStep(0); }}
          className="px-6 py-2.5 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
        >
          Start Wizard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{vs.name}</h1>
        <button
          onClick={() => { setView('wizard'); setWizardStep(0); }}
          className="flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-muted)] border border-[var(--color-border)] rounded-lg hover:border-[var(--color-primary)] hover:text-[var(--color-text)] transition-all"
        >
          <Pencil className="w-3.5 h-3.5" /> Edit in Wizard
        </button>
      </div>

      {plan && report && <MetricsBar plan={plan} report={report} />}
      {report && <WarningsPanel warnings={report.warnings} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold mb-4">System Map</h3>
          <VsmDiagram config={config} />
        </div>
        <div className="space-y-8">
          {plan && (
            <>
              <div>
                <h3 className="text-lg font-semibold mb-4">Budget Allocation</h3>
                <BudgetChart allocations={plan.allocations} total={plan.total_monthly_usd} />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">Model Routing</h3>
                <ModelRouting routing={plan.model_routing} />
              </div>
            </>
          )}
        </div>
      </div>

      {report && <ViabilityChecklist checks={report.checks} />}
      {plan && <AgentCards config={config} plan={plan} />}
      <HitlSummary config={config} />
      <ExportPanel config={config} />
    </div>
  );
}
