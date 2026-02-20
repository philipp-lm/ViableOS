import { useState } from 'react';
import { Plus } from 'lucide-react';
import { MultiSelectChips } from './MultiSelectChips';

interface Props {
  label: string;
  presetOptions: string[];
  selected: string[];
  onChange: (items: string[]) => void;
  placeholder?: string;
}

export function ChipsWithFreeText({ label, presetOptions, selected, onChange, placeholder = 'Add custom item...' }: Props) {
  const [custom, setCustom] = useState('');
  const customItems = selected.filter((s) => !presetOptions.includes(s));

  const addCustom = () => {
    const trimmed = custom.trim();
    if (!trimmed || selected.includes(trimmed)) return;
    onChange([...selected, trimmed]);
    setCustom('');
  };

  return (
    <div>
      <MultiSelectChips
        label={label}
        options={presetOptions}
        selected={selected}
        onChange={onChange}
      />
      {customItems.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {customItems.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs bg-[var(--color-secondary)] text-white"
            >
              {item}
              <button
                type="button"
                onClick={() => onChange(selected.filter((s) => s !== item))}
                className="hover:text-red-200"
              >&times;</button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-2 mt-2">
        <input
          type="text"
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustom())}
          placeholder={placeholder}
          className="flex-1 px-3 py-1.5 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text)] text-xs focus:outline-none focus:border-[var(--color-primary)]"
        />
        <button
          type="button"
          onClick={addCustom}
          disabled={!custom.trim()}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs bg-[var(--color-card)] border border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)] hover:text-[var(--color-text)] transition-all disabled:opacity-40"
        >
          <Plus className="w-3 h-3" /> Add
        </button>
      </div>
    </div>
  );
}
