import { StepHeader } from '../ui/StepHeader';
import { NavButtons } from '../ui/NavButtons';
import { ChipsWithFreeText } from '../ui/ChipsWithFreeText';
import { InfoCallout } from '../ui/InfoCallout';
import { useConfigStore } from '../../store/useConfigStore';
import { usePresets } from '../../hooks/useApiData';

export function IdentityStep() {
  const { config, updateVs, setWizardStep } = useConfigStore();
  const presets = usePresets();
  const vs = config.viable_system;
  const identity = vs.identity;

  const update = (field: string, value: unknown) => {
    updateVs({ identity: { ...identity, [field]: value } });
  };

  return (
    <div>
      <StepHeader
        step={1}
        title="Your Organization"
        subtitle="Define who your AI team is and what it stands for."
      />

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-1">
            Organization name
          </label>
          <input
            type="text"
            value={vs.name}
            onChange={(e) => updateVs({ name: e.target.value })}
            placeholder="e.g. My SaaS Startup"
            className="w-full px-3 py-2 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-muted)] mb-1">
            Purpose
          </label>
          <textarea
            value={identity.purpose}
            onChange={(e) => update('purpose', e.target.value)}
            placeholder="What is your system for?"
            rows={2}
            className="w-full px-3 py-2 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)] resize-none"
          />
        </div>

        {presets && (
          <>
            <ChipsWithFreeText
              label="Core values"
              presetOptions={presets.values}
              selected={identity.values ?? []}
              onChange={(v) => update('values', v)}
              placeholder="Add custom value..."
            />

            <div>
              <ChipsWithFreeText
                label="What should your agents NEVER do?"
                presetOptions={presets.never_do_presets}
                selected={identity.never_do ?? []}
                onChange={(v) => update('never_do', v)}
                placeholder="Add custom boundary..."
              />
              <InfoCallout title="Community insight">
                Explicit boundaries prevent the most common agent failures. Be strict now, loosen later.
              </InfoCallout>
            </div>
          </>
        )}
      </div>

      <NavButtons
        onBack={() => setWizardStep(0)}
        onNext={() => setWizardStep(2)}
        nextDisabled={!vs.name || !identity.purpose}
      />
    </div>
  );
}
