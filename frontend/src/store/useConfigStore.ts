import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Config, ViableSystem } from '../types';
import { api } from '../api/client';

const EMPTY_CONFIG: Config = {
  viable_system: {
    name: '',
    identity: { purpose: '' },
    system_1: [],
  },
};

interface ConfigStore {
  config: Config;
  wizardStep: number;
  view: 'wizard' | 'dashboard';
  templateKey: string | null;

  setConfig: (config: Config) => void;
  updateVs: (partial: Partial<ViableSystem>) => void;
  loadTemplate: (key: string) => Promise<void>;
  setWizardStep: (step: number) => void;
  setView: (view: 'wizard' | 'dashboard') => void;
  resetConfig: () => void;
}

export const useConfigStore = create<ConfigStore>()(
  persist(
    (set, get) => ({
      config: EMPTY_CONFIG,
      wizardStep: 0,
      view: 'wizard',
      templateKey: null,

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

      resetConfig: () => set({ config: EMPTY_CONFIG, templateKey: null, wizardStep: 0, view: 'wizard' }),
    }),
    {
      name: 'viableos-store',
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
);
