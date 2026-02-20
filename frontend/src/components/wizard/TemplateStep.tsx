import { StepHeader } from '../ui/StepHeader';
import { Card } from '../ui/Card';
import { useTemplates } from '../../hooks/useApiData';
import { useConfigStore } from '../../store/useConfigStore';
import { Layers, Plus } from 'lucide-react';

export function TemplateStep() {
  const templates = useTemplates();
  const { templateKey, loadTemplate, setWizardStep } = useConfigStore();

  const handleSelect = async (key: string) => {
    await loadTemplate(key);
    setWizardStep(1);
  };

  return (
    <div>
      <StepHeader
        step={0}
        title="Choose a Template"
        subtitle="Pick a starting point for your AI organization. You can customize everything later."
      />
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
