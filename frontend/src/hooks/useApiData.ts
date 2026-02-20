import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { BudgetPlan, ModelInfo, Presets, Template, ViabilityReport, Config } from '../types';

export function useTemplates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  useEffect(() => { api.getTemplates().then(setTemplates); }, []);
  return templates;
}

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  useEffect(() => { api.getModels().then(setModels); }, []);
  return models;
}

export function usePresets() {
  const [presets, setPresets] = useState<Presets | null>(null);
  useEffect(() => { api.getPresets().then(setPresets); }, []);
  return presets;
}

export function useBudget(config: Config) {
  const [plan, setPlan] = useState<BudgetPlan | null>(null);
  const vs = config.viable_system;
  const budgetKey = JSON.stringify({
    budget: vs.budget,
    routing: vs.model_routing,
    units: vs.system_1?.map((u) => ({ name: u.name, model: u.model, weight: u.weight })),
  });

  useEffect(() => {
    if (!vs.budget?.monthly_usd) return;
    const timer = setTimeout(() => {
      api.calculateBudget(config).then(setPlan).catch(() => {});
    }, 300);
    return () => clearTimeout(timer);
  }, [budgetKey]);

  return plan;
}

export function useViabilityCheck(config: Config) {
  const [report, setReport] = useState<ViabilityReport | null>(null);
  const configKey = JSON.stringify(config);

  useEffect(() => {
    const timer = setTimeout(() => {
      api.checkViability(config).then(setReport).catch(() => {});
    }, 300);
    return () => clearTimeout(timer);
  }, [configKey]);

  return report;
}
