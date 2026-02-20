import type { Config } from '../../types';

const COLORS = {
  s5: { bg: 'linear-gradient(135deg, #312e81, #3730a3)', border: '#6366f1', badge: '#6366f1', text: '#c7d2fe' },
  s4: { bg: 'linear-gradient(135deg, #164e63, #155e75)', border: '#06b6d4', badge: '#06b6d4', text: '#a5f3fc' },
  s3star: { bg: 'linear-gradient(135deg, #831843, #9d174d)', border: '#ec4899', badge: '#ec4899', text: '#fbcfe8' },
  s3: { bg: 'linear-gradient(135deg, #78350f, #92400e)', border: '#f59e0b', badge: '#f59e0b', text: '#fde68a' },
  s2: { bg: 'linear-gradient(135deg, #14532d, #166534)', border: '#10b981', badge: '#10b981', text: '#a7f3d0' },
  s1: { bg: 'linear-gradient(135deg, #1e293b, #334155)', border: '#94a3b8', badge: '#64748b', text: '#cbd5e1' },
};

function SystemBox({
  label,
  title,
  children,
  colorKey,
  dimmed,
  className = '',
}: {
  label: string;
  title: string;
  children: React.ReactNode;
  colorKey: keyof typeof COLORS;
  dimmed?: boolean;
  className?: string;
}) {
  const c = COLORS[colorKey];
  return (
    <div
      className={`rounded-xl p-4 transition-opacity ${className}`}
      style={{
        background: c.bg,
        border: `2px solid ${c.border}`,
        opacity: dimmed ? 0.5 : 1,
      }}
    >
      <span
        className="inline-block text-[10px] font-bold px-2 py-0.5 rounded text-white tracking-wide mb-1.5"
        style={{ background: c.badge }}
      >
        {label}
      </span>
      <div className="text-sm font-bold mb-1" style={{ color: c.text }}>
        {title}
      </div>
      <div className="text-[11px] leading-relaxed" style={{ color: c.text }}>
        {children}
      </div>
    </div>
  );
}

interface Props {
  config: Config;
}

export function VsmDiagram({ config }: Props) {
  const vs = config.viable_system;
  const identity = vs.identity;
  const units = vs.system_1;
  const rules = vs.system_2?.coordination_rules ?? [];
  const s3 = vs.system_3 ?? {};
  const s3star = vs.system_3_star ?? {};
  const s4 = vs.system_4 ?? {};
  const hitl = vs.human_in_the_loop ?? {};
  const neverDo = identity.never_do ?? [];

  const hasS2 = rules.length > 0;
  const hasS3 = !!(s3.reporting_rhythm || s3.resource_allocation);
  const hasS3star = (s3star.checks?.length ?? 0) > 0;
  const hasS4 = !!(s4.monitoring?.competitors?.length || s4.monitoring?.technology?.length);

  return (
    <div className="grid grid-cols-2 gap-2.5">
      <SystemBox label="S5" title="Identity & Policy" colorKey="s5">
        <div>{identity.purpose?.slice(0, 80)}</div>
        <div className="mt-1 text-[10px] opacity-80">
          Values: {identity.values?.slice(0, 3).join(', ') || '—'}
        </div>
        <div className="text-[10px] opacity-80">
          {hitl.approval_required?.length ?? 0} approval gates | {hitl.emergency_alerts?.length ?? 0} emergency alerts
        </div>
        {neverDo.length > 0 && (
          <div className="text-[10px] text-red-300 mt-1">{neverDo.length} hard boundaries</div>
        )}
      </SystemBox>

      <SystemBox label="S4" title="Intelligence (Scout)" colorKey="s4" dimmed={!hasS4}>
        {hasS4 ? (
          [...(s4.monitoring?.competitors?.slice(0, 2) ?? []), ...(s4.monitoring?.technology?.slice(0, 2) ?? [])].map((item, i) => (
            <div key={i} className="pl-3 relative">
              <span className="absolute left-0 font-bold">&rsaquo;</span> {item}
            </div>
          ))
        ) : (
          <div className="italic opacity-50">Not configured yet</div>
        )}
      </SystemBox>

      <SystemBox label="S3*" title="Audit" colorKey="s3star" dimmed={!hasS3star}>
        <div className="text-[10px] opacity-80 mb-1">
          Independent verification — different AI provider
        </div>
        {hasS3star ? (
          s3star.checks?.slice(0, 3).map((c, i) => (
            <div key={i} className="pl-3 relative">
              <span className="absolute left-0 font-bold">&rsaquo;</span>
              <strong>{c.name}</strong> &rarr; {c.target}
            </div>
          ))
        ) : (
          <div className="italic opacity-50">Not configured yet</div>
        )}
      </SystemBox>

      <SystemBox label="S3" title="Optimization (Manager)" colorKey="s3" dimmed={!hasS3}>
        <div>Reporting: {s3.reporting_rhythm ?? '—'}</div>
        <div>Resources: {s3.resource_allocation?.slice(0, 60) ?? '—'}</div>
      </SystemBox>

      <SystemBox label="S1" title={`Operations — ${units.length} unit${units.length !== 1 ? 's' : ''}`} colorKey="s1" className="col-span-2">
        {units.map((u, i) => (
          <div key={i} className="flex items-baseline gap-1.5 py-0.5">
            <span className="text-[8px] text-[#94a3b8]">&#x25cf;</span>
            <strong className="text-[var(--color-text)]">{u.name}</strong>
            <span>— {u.purpose?.slice(0, 50)}</span>
          </div>
        ))}
      </SystemBox>

      <SystemBox label="S2" title="Coordination" colorKey="s2" dimmed={!hasS2} className="col-span-2">
        {hasS2 ? (
          rules.slice(0, 4).map((r, i) => (
            <div key={i} className="pl-3 relative leading-snug py-0.5">
              <span className="absolute left-0 font-bold">&rsaquo;</span>
              {r.trigger} &rarr; {r.action}
            </div>
          ))
        ) : (
          <div className="italic opacity-50">Auto-generated rules will be applied at export</div>
        )}
        {rules.length > 4 && (
          <div className="text-[10px] opacity-60 mt-1">+ {rules.length - 4} more rules</div>
        )}
      </SystemBox>
    </div>
  );
}
