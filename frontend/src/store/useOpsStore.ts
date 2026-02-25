import { create } from 'zustand';
import type {
  RuntimeType,
  OpsAgent,
  OpsActivity,
  OpsSignal,
  OpsWorkPackage,
  OpsDecision,
} from '../types';

interface OpsStore {
  // Connection
  runtime: RuntimeType;
  url: string;
  apiKey: string;
  connected: boolean;
  connecting: boolean;
  error: string | null;

  // Data
  agents: OpsAgent[];
  activity: OpsActivity[];
  signals: OpsSignal[];
  workPackages: OpsWorkPackage[];
  decisions: OpsDecision[];

  // Polling
  pollingInterval: ReturnType<typeof setInterval> | null;

  // Actions
  setRuntime: (runtime: RuntimeType) => void;
  setUrl: (url: string) => void;
  setApiKey: (apiKey: string) => void;
  setConnected: (connected: boolean) => void;
  setConnecting: (connecting: boolean) => void;
  setError: (error: string | null) => void;
  setAgents: (agents: OpsAgent[]) => void;
  setActivity: (activity: OpsActivity[]) => void;
  setSignals: (signals: OpsSignal[]) => void;
  setWorkPackages: (workPackages: OpsWorkPackage[]) => void;
  setDecisions: (decisions: OpsDecision[]) => void;
  setPollingInterval: (interval: ReturnType<typeof setInterval> | null) => void;
  disconnect: () => void;
}

export const useOpsStore = create<OpsStore>()((set, get) => ({
  runtime: 'openclaw',
  url: '',
  apiKey: '',
  connected: false,
  connecting: false,
  error: null,

  agents: [],
  activity: [],
  signals: [],
  workPackages: [],
  decisions: [],

  pollingInterval: null,

  setRuntime: (runtime) => set({ runtime }),
  setUrl: (url) => set({ url }),
  setApiKey: (apiKey) => set({ apiKey }),
  setConnected: (connected) => set({ connected }),
  setConnecting: (connecting) => set({ connecting }),
  setError: (error) => set({ error }),
  setAgents: (agents) => set({ agents }),
  setActivity: (activity) => set({ activity }),
  setSignals: (signals) => set({ signals }),
  setWorkPackages: (workPackages) => set({ workPackages }),
  setDecisions: (decisions) => set({ decisions }),
  setPollingInterval: (pollingInterval) => set({ pollingInterval }),

  disconnect: () => {
    const interval = get().pollingInterval;
    if (interval) clearInterval(interval);
    set({
      connected: false,
      connecting: false,
      error: null,
      agents: [],
      activity: [],
      signals: [],
      workPackages: [],
      decisions: [],
      pollingInterval: null,
    });
  },
}));
