import { StepHeader } from '../ui/StepHeader';
import { Card } from '../ui/Card';
import { useTemplates } from '../../hooks/useApiData';
import { useConfigStore } from '../../store/useConfigStore';
import { useChatStore } from '../../store/useChatStore';
import { Layers, Plus, MessageSquare } from 'lucide-react';

export function TemplateStep() {
  const templates = useTemplates();
  const { templateKey, loadTemplate, setWizardStep, assessmentData, loadFromAssessment, setConfig } = useConfigStore();
  const chatAssessment = useChatStore((s) => s.assessmentData);

  const handleSelect = async (key: string) => {
    await loadTemplate(key);
    setWizardStep(1);
  };

  const handleUseAssessment = async () => {
    const assessment = assessmentData || chatAssessment;
    if (!assessment) return;
    try {
      const API_BASE = import.meta.env.VITE_API_URL || '/api';
      const res = await fetch(`${API_BASE}/assessment/transform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessment),
      });
      if (res.ok) {
        const config = await res.json();
        setConfig(config);
        setWizardStep(1);
      }
    } catch {
      // ignore
    }
  };

  const hasAssessment = !!(assessmentData || chatAssessment);
  const assessmentName = (assessmentData || chatAssessment)?.system_name;
  const assessmentUnits = (() => {
    const data = assessmentData || chatAssessment;
    if (!data) return 0;
    const levels = data.recursion_levels as Record<string, { operational_units?: unknown[] }> | undefined;
    return levels?.level_0?.operational_units?.length || 0;
  })();

  return (
    <div>
      <StepHeader
        step={0}
        title="Choose a Template"
        subtitle="Pick a starting point for your AI organization. You can customize everything later."
      />

      {hasAssessment && (
        <div className="mb-4">
          <Card onClick={handleUseAssessment} active={templateKey === 'assessment'}>
            <div className="flex items-start gap-2">
              <MessageSquare className="w-4 h-4 mt-0.5 text-[var(--color-accent)]" />
              <div>
                <div className="font-semibold text-sm text-[var(--color-accent)]">From Chat Assessment</div>
                <div className="text-xs text-[var(--color-muted)] mt-0.5">
                  {assessmentName || 'Assessment'} — {assessmentUnits} units detected
                </div>
                <div className="text-xs text-[var(--color-muted)] mt-0.5 opacity-70">
                  Pre-fills the wizard with data from your VSM Expert Chat conversation
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {templates.map((t) => (
          <Card
            key={t.key}
            onClick={() => handleSelect(t.key)}
            active={templateKey === t.key}
          >
            <div className="flex items-start gap-2">
              {t.key === 'custom' ? (
                <Plus className="w-4 h-4 mt-0.5 text-[var(--color-primary)]" />
              ) : (
                <Layers className="w-4 h-4 mt-0.5 text-[var(--color-muted)]" />
              )}
              <div>
                <div className="font-semibold text-sm text-[var(--color-text)]">{t.name}</div>
                <div className="text-xs text-[var(--color-muted)] mt-0.5">{t.tagline}</div>
                {t.units > 0 && (
                  <div className="text-xs text-[var(--color-muted)] mt-1 opacity-70">
                    {t.units} units
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
