import { StepHeader } from '../ui/StepHeader';
import { NavButtons } from '../ui/NavButtons';
import { ChipsWithFreeText } from '../ui/ChipsWithFreeText';
import { useConfigStore } from '../../store/useConfigStore';
import { usePresets } from '../../hooks/useApiData';

export function HitlStep() {
  const { config, updateVs, setWizardStep } = useConfigStore();
  const presets = usePresets();
  const vs = config.viable_system;
  const hitl = vs.human_in_the_loop ?? {};
  const persistence = vs.persistence ?? { strategy: 'none' };

  const updateHitl = (field: string, value: unknown) => {
    updateVs({ human_in_the_loop: { ...hitl, [field]: value } });
  };

  return (
    <div>
      <StepHeader
        step={4}
        title="Human-in-the-Loop & Persistence"
        subtitle="Define what needs your approval and how agents persist state."
      />

      {presets && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">
              Notification channel
            </label>
            <div className="flex gap-2">
              {presets.notification_channels.map((ch) => (
                <button
                  key={ch}
                  onClick={() => updateHitl('notification_channel', ch)}
                  className={`px-3 py-1.5 rounded-lg text-sm capitalize border transition-all ${
                    hitl.notification_channel === ch
                      ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-text)]'
                      : 'border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]'
                  }`}
                >
                  {ch}
                </button>
              ))}
            </div>
          </div>

          <ChipsWithFreeText
            label="Needs your approval (blocks until you approve)"
            presetOptions={presets.approval_presets}
            selected={hitl.approval_required ?? []}
            onChange={(v) => updateHitl('approval_required', v)}
          />

          <ChipsWithFreeText
            label="Sent for review (proceeds, you review later)"
            presetOptions={presets.review_presets}
            selected={hitl.review_required ?? []}
            onChange={(v) => updateHitl('review_required', v)}
          />

          <ChipsWithFreeText
            label="Emergency alerts"
            presetOptions={presets.emergency_presets}
            selected={hitl.emergency_alerts ?? []}
            onChange={(v) => updateHitl('emergency_alerts', v)}
          />

          <div className="border-t border-[var(--color-border)] pt-6">
            <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">
              State persistence
            </label>
            <div className="space-y-2">
              {Object.entries(presets.persistence_strategies).map(([key, desc]) => (
                <label
                  key={key}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                    persistence.strategy === key
                      ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
                      : 'border-[var(--color-border)] bg-[var(--color-card)] hover:border-[var(--color-primary)]'
                  }`}
                >
                  <input
                    type="radio"
                    name="persistence"
                    checked={persistence.strategy === key}
                    onChange={() => updateVs({ persistence: { strategy: key } })}
                    className="mt-1 accent-[var(--color-primary)]"
                  />
                  <div>
                    <div className="text-sm font-medium text-[var(--color-text)] capitalize">{key}</div>
                    <div className="text-xs text-[var(--color-muted)]">{desc}</div>
                  </div>
                </label>
              ))}
            </div>

            {persistence.strategy && persistence.strategy !== 'none' && persistence.strategy !== 'custom' && (
              <div className="mt-3">
                <label className="block text-xs text-[var(--color-muted)] mb-1">Storage path</label>
                <input
                  type="text"
                  value={persistence.path ?? ''}
                  onChange={(e) => updateVs({ persistence: { ...persistence, path: e.target.value } })}
                  placeholder="e.g. ./data/state.db"
                  className="w-full px-3 py-2 rounded-lg bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
                />
              </div>
            )}
          </div>
        </div>
      )}

      <NavButtons onBack={() => setWizardStep(3)} onNext={() => setWizardStep(5)} />
    </div>
  );
}
