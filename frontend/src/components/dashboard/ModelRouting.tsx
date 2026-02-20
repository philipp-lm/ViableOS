const FRIENDLY: Record<string, string> = {
  s1_routine: 'S1 Routine',
  s1_complex: 'S1 Complex',
  s2_coordination: 'S2 Coordinator',
  s3_optimization: 'S3 Optimizer',
  s3_star_audit: 'S3* Auditor',
  s4_intelligence: 'S4 Scout',
  s5_preparation: 'S5 Guardian',
};

const TIER_COLORS: Record<string, string> = {
  haiku: 'var(--color-success)',
  mini: 'var(--color-success)',
  flash: 'var(--color-success)',
  sonnet: 'var(--color-warning)',
  'gpt-5.1': 'var(--color-warning)',
  'gpt-5.2': 'var(--color-danger)',
  opus: 'var(--color-danger)',
  o3: 'var(--color-danger)',
  pro: 'var(--color-danger)',
};

function getTierColor(model: string): string {
  const lower = model.toLowerCase();
  for (const [key, color] of Object.entries(TIER_COLORS)) {
    if (lower.includes(key)) return color;
  }
  return 'var(--color-muted)';
}

interface Props {
  routing: Record<string, string>;
}

export function ModelRouting({ routing }: Props) {
  const keys = ['s1_routine', 's1_complex', 's2_coordination', 's3_optimization', 's3_star_audit', 's4_intelligence', 's5_preparation'];

  return (
    <div className="space-y-2">
      {keys.map((key) => {
        const model = routing[key] ?? 'unknown';
        const modelShort = model.includes('/') ? model.split('/')[1] : model;
        const color = getTierColor(model);

        return (
          <div key={key} className="flex items-center gap-3">
            <span className="text-xs text-[var(--color-muted)] w-24 shrink-0">
              {FRIENDLY[key] ?? key}
            </span>
            <div className="flex-1 h-7 rounded-md overflow-hidden" style={{ background: `${color}20` }}>
              <div
                className="h-full rounded-md flex items-center px-2.5 text-xs text-white font-medium"
                style={{ background: color, width: '100%' }}
              >
                {modelShort}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
