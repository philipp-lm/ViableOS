import type { BudgetPlan, Config } from '../../types';

const MANAGEMENT_AGENTS = [
  { name: 'Coordinator', sysKey: 'S2', routingKey: 's2_coordination', purpose: 'Prevents conflicts between units' },
  { name: 'Optimizer', sysKey: 'S3', routingKey: 's3_optimization', purpose: 'Allocates resources, weekly digest' },
  { name: 'Auditor', sysKey: 'S3*', routingKey: 's3_star_audit', purpose: 'Independent quality verification' },
  { name: 'Scout', sysKey: 'S4', routingKey: 's4_intelligence', purpose: 'Monitors environment, strategic briefs' },
  { name: 'Policy Guardian', sysKey: 'S5', routingKey: 's5_preparation', purpose: 'Enforces values and policies' },
];

interface Props {
  config: Config;
  plan: BudgetPlan;
}

export function AgentCards({ config, plan }: Props) {
  const units = config.viable_system.system_1;

  const agents = [
    ...units.map((u) => {
      const alloc = plan.allocations.find((a) => a.system === `S1:${u.name}`);
      return {
        name: u.name,
        role: 'Operations (S1)',
        purpose: u.purpose,
        model: alloc?.model ?? '?',
        budget: alloc ? `$${alloc.monthly_usd.toFixed(0)}` : '?',
        tools: u.tools?.slice(0, 4).join(', ') ?? '',
      };
    }),
    ...MANAGEMENT_AGENTS.map((ma) => {
      const alloc = plan.allocations.find((a) => a.system === ma.sysKey);
      return {
        name: ma.name,
        role: `${ma.sysKey}`,
        purpose: ma.purpose,
        model: plan.model_routing[ma.routingKey] ?? '?',
        budget: alloc ? `$${alloc.monthly_usd.toFixed(0)}` : '?',
        tools: '',
      };
    }),
  ];

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Agent Overview</h3>
      <div className="grid grid-cols-3 gap-3">
        {agents.map((agent) => {
          const modelShort = agent.model.includes('/') ? agent.model.split('/')[1] : agent.model;
          return (
            <div
              key={`${agent.role}-${agent.name}`}
              className="p-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)]"
            >
              <div className="font-bold text-sm text-[var(--color-text)]">{agent.name}</div>
              <div className="text-[10px] text-[var(--color-muted)] mb-1">{agent.role}</div>
              <div className="text-xs text-[#cbd5e1] mb-2">{agent.purpose}</div>
              <div className="text-[10px] text-[var(--color-muted)]">
                Model:{' '}
                <span className="font-mono bg-[var(--color-bg)] px-1.5 py-0.5 rounded text-[var(--color-muted)]">
                  {modelShort}
                </span>
                <span className="ml-2">{agent.budget}/mo</span>
              </div>
              {agent.tools && (
                <div className="text-[10px] text-[var(--color-muted)] mt-1">Tools: {agent.tools}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
