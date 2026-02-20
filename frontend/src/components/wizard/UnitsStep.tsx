import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { StepHeader } from '../ui/StepHeader';
import { NavButtons } from '../ui/NavButtons';
import { InfoCallout } from '../ui/InfoCallout';
import { useConfigStore } from '../../store/useConfigStore';
import { usePresets } from '../../hooks/useApiData';
import type { S1Unit } from '../../types';

function ToolSelector({
  unit,
  index,
  onUpdate,
  toolCategories,
}: {
  unit: S1Unit;
  index: number;
  onUpdate: (i: number, u: S1Unit) => void;
  toolCategories: Record<string, string[]>;
}) {
  const [customTool, setCustomTool] = useState('');
  const allPresetTools = Object.values(toolCategories).flat();
  const customTools = (unit.tools ?? []).filter((t) => !allPresetTools.includes(t));

  const addCustomTool = () => {
    const trimmed = customTool.trim();
    if (!trimmed || unit.tools?.includes(trimmed)) return;
    onUpdate(index, { ...unit, tools: [...(unit.tools ?? []), trimmed] });
    setCustomTool('');
  };

  return (
    <div>
      <label className="block text-xs text-[var(--color-muted)] mb-1">Tools</label>
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(toolCategories).map(([category, tools]) => (
          <details key={category} className="text-xs">
            <summary className="cursor-pointer text-[var(--color-muted)] hover:text-[var(--color-text)] px-2 py-1 rounded bg-[var(--color-bg)] border border-[var(--color-border)]">
              {category}
            </summary>
            <div className="flex flex-wrap gap-1 mt-1 ml-2">
              {tools.map((tool) => {
                const active = unit.tools?.includes(tool);
                return (
                  <button
                    key={tool}
                    type="button"
                    onClick={() => {
                      const current = unit.tools ?? [];
                      onUpdate(index, {
                        ...unit,
                        tools: active ? current.filter((t) => t !== tool) : [...current, tool],
                      });
                    }}
                    className={`px-2 py-0.5 rounded text-xs transition-all border ${
                      active
                        ? 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white'
                        : 'border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]'
                    }`}
                  >
                    {tool}
                  </button>
                );
              })}
            </div>
          </details>
        ))}
      </div>
      {customTools.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {customTools.map((tool) => (
            <span
              key={tool}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-[var(--color-secondary)] text-white"
            >
              {tool}
              <button
                type="button"
                onClick={() => onUpdate(index, { ...unit, tools: (unit.tools ?? []).filter((t) => t !== tool) })}
                className="hover:text-red-200"
              >&times;</button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-2 mt-2">
        <input
          type="text"
          value={customTool}
          onChange={(e) => setCustomTool(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomTool())}
          placeholder="Add custom tool..."
          className="flex-1 px-2.5 py-1.5 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-xs focus:outline-none focus:border-[var(--color-primary)]"
        />
        <button
          type="button"
          onClick={addCustomTool}
          disabled={!customTool.trim()}
          className="px-3 py-1.5 rounded-lg text-xs bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)] hover:text-[var(--color-text)] transition-all disabled:opacity-40"
        >
          Add
        </button>
      </div>
    </div>
  );
}

function UnitEditor({
  unit,
  index,
  onUpdate,
  onRemove,
  autonomyLevels,
  toolCategories,
}: {
  unit: S1Unit;
  index: number;
  onUpdate: (i: number, u: S1Unit) => void;
  onRemove: (i: number) => void;
  autonomyLevels: Record<string, string>;
  toolCategories: Record<string, string[]>;
}) {
  return (
    <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase text-[var(--color-muted)] tracking-wider">
          Unit {index + 1}
        </span>
        <button
          onClick={() => onRemove(index)}
          className="text-[var(--color-muted)] hover:text-[var(--color-danger)] transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <input
          type="text"
          value={unit.name}
          onChange={(e) => onUpdate(index, { ...unit, name: e.target.value })}
          placeholder="Name"
          className="px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
        />
        <input
          type="text"
          value={unit.purpose}
          onChange={(e) => onUpdate(index, { ...unit, purpose: e.target.value })}
          placeholder="Purpose"
          className="px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
        />
      </div>

      <div>
        <label className="block text-xs text-[var(--color-muted)] mb-1">Autonomy</label>
        <select
          value={unit.autonomy ?? 'report'}
          onChange={(e) => onUpdate(index, { ...unit, autonomy: e.target.value })}
          className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-sm focus:outline-none focus:border-[var(--color-primary)]"
        >
          {Object.entries(autonomyLevels).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      <ToolSelector unit={unit} index={index} onUpdate={onUpdate} toolCategories={toolCategories} />
    </div>
  );
}

export function UnitsStep() {
  const { config, updateVs, setWizardStep } = useConfigStore();
  const presets = usePresets();
  const units = config.viable_system.system_1;

  const updateUnit = (i: number, u: S1Unit) => {
    const next = [...units];
    next[i] = u;
    updateVs({ system_1: next });
  };

  const removeUnit = (i: number) => {
    updateVs({ system_1: units.filter((_, idx) => idx !== i) });
  };

  const addUnit = () => {
    updateVs({
      system_1: [...units, { name: '', purpose: '', autonomy: 'report', tools: [] }],
    });
  };

  return (
    <div>
      <StepHeader
        step={2}
        title="Customize Your Teams"
        subtitle="Define the operational units (S1 agents) that do the actual work."
      />

      <InfoCallout title="Community insight: Start small">
        Start with 1-2 units. Get them working end-to-end before adding more. The community reports
        2+ weeks of tuning per agent.
      </InfoCallout>

      <div className="space-y-4 mt-6">
        {units.map((unit, i) => (
          <UnitEditor
            key={i}
            unit={unit}
            index={i}
            onUpdate={updateUnit}
            onRemove={removeUnit}
            autonomyLevels={presets?.autonomy_levels ?? {}}
            toolCategories={presets?.tool_categories ?? {}}
          />
        ))}

        <button
          onClick={addUnit}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-[var(--color-border)] text-[var(--color-muted)] text-sm hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-all"
        >
          <Plus className="w-4 h-4" /> Add unit
        </button>
      </div>

      <NavButtons
        onBack={() => setWizardStep(1)}
        onNext={() => setWizardStep(3)}
        nextDisabled={units.length === 0 || units.some((u) => !u.name || !u.purpose)}
      />
    </div>
  );
}
