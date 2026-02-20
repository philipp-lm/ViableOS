import type {
  BudgetPlan,
  Config,
  CoordinationRule,
  ModelInfo,
  Presets,
  Template,
  ViabilityReport,
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
  getTemplates: () => get<Template[]>('/templates'),
  getTemplate: (key: string) => get<Config>(`/templates/${key}`),
  getModels: () => get<ModelInfo[]>('/models'),
  getModelsByProvider: (provider: string) => get<string[]>(`/models/${provider}`),
  getPresets: () => get<Presets>('/presets'),
  validate: (config: Config) => post<string[]>('/validate', config),
  calculateBudget: (config: Config) => post<BudgetPlan>('/budget', config),
  checkViability: (config: Config) => post<ViabilityReport>('/check', config),
  generateRules: (units: Array<Record<string, unknown>>) =>
    post<CoordinationRule[]>('/coordination/rules', units),
  generatePackage: (config: Config) => postBlob('/generate', config),
};
