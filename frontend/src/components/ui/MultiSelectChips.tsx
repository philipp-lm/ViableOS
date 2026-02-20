import { Check } from 'lucide-react';

interface Props {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label?: string;
}

export function MultiSelectChips({ options, selected, onChange, label }: Props) {
  const toggle = (item: string) => {
    onChange(
      selected.includes(item)
        ? selected.filter((s) => s !== item)
        : [...selected, item]
    );
  };

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-[var(--color-muted)] mb-2">
          {label}
        </label>
      )}
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = selected.includes(opt);
          return (
            <button
              key={opt}
              type="button"
              onClick={() => toggle(opt)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-all border ${
                active
                  ? 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white'
                  : 'bg-[var(--color-card)] border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]'
              }`}
            >
              {active && <Check className="inline w-3 h-3 mr-1" />}
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
