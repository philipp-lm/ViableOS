export interface Template {
  key: string;
  name: string;
  tagline: string;
  description: string;
  units: number;
}

export interface S1Unit {
  name: string;
  purpose: string;
  autonomy?: string;
  tools?: string[];
  model?: string;
  weight?: number;
}

export interface Identity {
  purpose: string;
  values?: string[];
  never_do?: string[];
  decisions_requiring_human?: string[];
}

export interface CoordinationRule {
  trigger: string;
  action: string;
  scope?: string;
}

export interface HumanInTheLoop {
  notification_channel?: string;
  approval_required?: string[];
  review_required?: string[];
  emergency_alerts?: string[];
}

export interface Budget {
  monthly_usd: number;
  strategy: string;
  alerts?: {
    warn_at_percent?: number;
    auto_downgrade_at_percent?: number;
  };
}

export interface ModelRouting {
  provider_preference?: string;
  s1_routine?: string;
  s1_complex?: string;
  s2_coordination?: string;
  s3_optimization?: string;
  s3_star_audit?: string;
  s4_intelligence?: string;
  s5_preparation?: string;
  [key: string]: string | undefined;
}

export interface Persistence {
  strategy: string;
  path?: string;
}

export interface ViableSystem {
  name: string;
  runtime?: string;
  identity: Identity;
  system_1: S1Unit[];
  system_2?: {
    coordination_rules?: CoordinationRule[];
  };
  system_3?: {
    reporting_rhythm?: string;
    resource_allocation?: string;
  };
  system_3_star?: {
    checks?: Array<{ name: string; target: string; on_failure?: string }>;
  };
  system_4?: {
    monitoring?: {
      competitors?: string[];
      technology?: string[];
      regulation?: string[];
    };
  };
  budget?: Budget;
  model_routing?: ModelRouting;
  human_in_the_loop?: HumanInTheLoop;
  persistence?: Persistence;
}

export interface Config {
  viable_system: ViableSystem;
}

export interface ModelInfo {
  id: string;
  provider: string;
  tier: string;
  note: string;
  agent_reliability: string;
  warning: string | null;
}

export interface BudgetAllocation {
  system: string;
  friendly_name: string;
  monthly_usd: number;
  model: string;
  percentage: number;
}

export interface BudgetPlan {
  total_monthly_usd: number;
  strategy: string;
  allocations: BudgetAllocation[];
  model_routing: Record<string, string>;
}

export interface CheckResult {
  system: string;
  name: string;
  present: boolean;
  details: string;
  suggestions: string[];
}

export interface Warning {
  category: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  suggestion: string;
}

export interface ViabilityReport {
  score: number;
  total: number;
  checks: CheckResult[];
  warnings: Warning[];
}

export interface Presets {
  values: string[];
  autonomy_levels: Record<string, string>;
  tool_categories: Record<string, string[]>;
  approval_presets: string[];
  review_presets: string[];
  emergency_presets: string[];
  notification_channels: string[];
  never_do_presets: string[];
  persistence_strategies: Record<string, string>;
  model_tiers: Record<string, string>;
  agent_reliability_labels: Record<string, string>;
  strategy_presets: string[];
}

// ── Chat Types ──────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AssessmentConfig {
  system_name: string;
  purpose: string;
  team?: { size: number; roles?: string[] };
  recursion_levels?: Record<string, unknown>;
  dependencies?: Record<string, unknown>;
  shared_resources?: string[];
  external_forces?: Array<{ name: string; type?: string; frequency?: string }>;
  metasystem?: Record<string, unknown>;
  success_criteria?: Array<{ criterion: string; priority: number }>;
  [key: string]: unknown;
}

// ── Ops Room Types ──────────────────────────────────────────

export type RuntimeType = 'openclaw' | 'langgraph';

export interface OpsConnection {
  runtime: RuntimeType;
  url: string;
  apiKey: string;
  connected: boolean;
}

export type AgentStatus = 'online' | 'working' | 'error' | 'offline';

export interface OpsAgent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  lastSeen?: string;
  currentTask?: string;
}

export interface OpsActivity {
  id: string;
  timestamp: string;
  agent: string;
  type: string;
  summary: string;
}

export interface OpsSignal {
  id: string;
  timestamp: string;
  source: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  message: string;
}

export interface OpsWorkPackage {
  id: string;
  title: string;
  assignee: string;
  status: 'queued' | 'active' | 'done';
  created: string;
}

export interface OpsDecision {
  id: string;
  title: string;
  description: string;
  requestedBy: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected';
}
