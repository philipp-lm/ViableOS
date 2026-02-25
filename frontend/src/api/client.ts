import type {
  BudgetPlan,
  Config,
  CoordinationRule,
  ModelInfo,
  Presets,
  Template,
  ViabilityReport,
  AssessmentConfig,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path}: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path}: ${res.status}`);
  return res.json();
}

async function postBlob(path: string, body: unknown): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path}: ${res.status}`);
  return res.blob();
}

export const api = {
  // Templates
  getTemplates: () => get<Template[]>('/templates'),
  getTemplate: (key: string) => get<Config>(`/templates/${key}`),

  // Models
  getModels: () => get<ModelInfo[]>('/models'),
  getModelsByProvider: (provider: string) => get<string[]>(`/models/${provider}`),

  // Presets
  getPresets: () => get<Presets>('/presets'),

  // Validation & Budget
  validate: (config: Config) => post<string[]>('/validate', config),
  calculateBudget: (config: Config) => post<BudgetPlan>('/budget', config),
  checkViability: (config: Config) => post<ViabilityReport>('/check', config),

  // Coordination
  generateRules: (units: Array<Record<string, unknown>>) =>
    post<CoordinationRule[]>('/coordination/rules', units),

  // Generation
  generatePackage: (config: Config) => postBlob('/generate', config),
  generateLanggraphPackage: (config: Config) => postBlob('/generate/langgraph', config),

  // Assessment
  transformAssessment: (assessment: AssessmentConfig) =>
    post<Config>('/assessment/transform', assessment),

  // Ops Room
  opsConnect: (runtime: string, url: string, apiKey: string) =>
    post<{ connected: boolean; error?: string }>('/ops/connect', { runtime, url, api_key: apiKey }),
  opsDisconnect: () => post<{ disconnected: boolean }>('/ops/disconnect', {}),
  opsAgents: () => get<Array<Record<string, unknown>>>('/ops/agents'),
  opsActivity: () => get<Array<Record<string, unknown>>>('/ops/activity'),
  opsSignals: () => get<Array<Record<string, unknown>>>('/ops/signals'),
  opsWorkPackages: () => get<Array<Record<string, unknown>>>('/ops/workpackages'),
  opsDecisions: () => get<Array<Record<string, unknown>>>('/ops/decisions'),
  opsResolveDecision: (id: string, action: string) =>
    post<Record<string, unknown>>(`/ops/decisions/${id}/resolve`, { action }),
};
