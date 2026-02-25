import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Config, ViableSystem, AssessmentConfig } from '../types';
import { api } from '../api/client';

const EMPTY_CONFIG: Config = {
  viable_system: {
    name: '',
    identity: { purpose: '' },
    system_1: [],
  },
};

type View = 'chat' | 'wizard' | 'dashboard' | 'opsroom';

interface ConfigStore {
  config: Config;
  wizardStep: number;
  view: View;
  templateKey: string | null;
  runtimeTarget: 'openclaw' | 'langgraph';
  assessmentData: AssessmentConfig | null;

  setConfig: (config: Config) => void;
  updateVs: (partial: Partial<ViableSystem>) => void;
  loadTemplate: (key: string) => Promise<void>;
  setWizardStep: (step: number) => void;
  setView: (view: View) => void;
  setRuntimeTarget: (target: 'openclaw' | 'langgraph') => void;
  setAssessmentData: (data: AssessmentConfig | null) => void;
  loadFromAssessment: (config: Config) => void;
  resetConfig: () => void;
}

export const useConfigStore = create<ConfigStore>()(
  persist(
    (set, get) => ({
      config: EMPTY_CONFIG,
      wizardStep: 0,
      view: 'chat',
      templateKey: null,
      runtimeTarget: 'openclaw',
      assessmentData: null,

      setConfig: (config) => set({ config }),

      updateVs: (partial) => {
        const current = get().config;
        set({
          config: {
            ...current,
            viable_system: { ...current.viable_system, ...partial },
          },
        });
      },

      loadTemplate: async (key) => {
        const config = await api.getTemplate(key);
        set({ config, templateKey: key });
      },

      setWizardStep: (wizardStep) => set({ wizardStep }),

      setView: (view) => set({ view }),

      setRuntimeTarget: (runtimeTarget) => set({ runtimeTarget }),

      setAssessmentData: (assessmentData) => set({ assessmentData }),

      loadFromAssessment: (config) => {
        set({ config, templateKey: 'assessment', wizardStep: 0 });
      },

      resetConfig: () => set({ config: EMPTY_CONFIG, templateKey: null, wizardStep: 0, view: 'chat', assessmentData: null }),
    }),
    {
      name: 'viableos-store',
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
);
