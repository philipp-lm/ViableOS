import { useState } from 'react';
import { Plug, Unplug } from 'lucide-react';
import { useOpsStore } from '../../store/useOpsStore';
import type { RuntimeType } from '../../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function ConnectionPanel() {
  const {
    runtime, url, apiKey, connected, connecting, error,
    setRuntime, setUrl, setApiKey, setConnected, setConnecting, setError,
    setAgents, setActivity, setSignals, setWorkPackages, setDecisions,
    setPollingInterval, disconnect,
  } = useOpsStore();

  const handleConnect = async () => {
    setConnecting(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/ops/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ runtime, url, api_key: apiKey }),
      });
      const data = await res.json();
      if (data.connected) {
        setConnected(true);
        startPolling();
      } else {
        setError(data.error || 'Connection failed');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Connection error');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`${API_BASE}/ops/disconnect`, { method: 'POST' });
    } catch {
      // ignore
    }
    disconnect();
  };

  const fetchAllData = async () => {
    try {
      const [agents, activity, signals, wp, decisions] = await Promise.all([
        fetch(`${API_BASE}/ops/agents`).then((r) => r.ok ? r.json() : []),
        fetch(`${API_BASE}/ops/activity`).then((r) => r.ok ? r.json() : []),
        fetch(`${API_BASE}/ops/signals`).then((r) => r.ok ? r.json() : []),
        fetch(`${API_BASE}/ops/workpackages`).then((r) => r.ok ? r.json() : []),
        fetch(`${API_BASE}/ops/decisions`).then((r) => r.ok ? r.json() : []),
      ]);
      setAgents(agents);
      setActivity(activity);
      setSignals(signals);
      setWorkPackages(wp);
      setDecisions(decisions);
    } catch {
      // ignore polling errors
    }
  };

  const startPolling = () => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    setPollingInterval(interval);
  };

  return (
    <div className="bg-[var(--color-card)] rounded-xl border border-[var(--color-border)] p-4">
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={runtime}
          onChange={(e) => setRuntime(e.target.value as RuntimeType)}
          disabled={connected}
          className="bg-[var(--color-bg)] text-[var(--color-text)] text-sm rounded-lg px-3 py-2 border border-[var(--color-border)] outline-none"
        >
          <option value="openclaw">OpenClaw</option>
          <option value="langgraph">LangGraph</option>
        </select>

        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={connected}
          placeholder={runtime === 'openclaw' ? 'http://localhost:3210' : 'http://localhost:8123'}
          className="flex-1 min-w-[200px] bg-[var(--color-bg)] text-[var(--color-text)] text-sm rounded-lg px-3 py-2 border border-[var(--color-border)] outline-none placeholder:text-[var(--color-muted)]"
        />

        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          disabled={connected}
          placeholder="API Key"
          className="w-48 bg-[var(--color-bg)] text-[var(--color-text)] text-sm rounded-lg px-3 py-2 border border-[var(--color-border)] outline-none placeholder:text-[var(--color-muted)]"
        />

        {connected ? (
          <button
            onClick={handleDisconnect}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-danger)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <Unplug className="w-4 h-4" />
            Disconnect
          </button>
        ) : (
          <button
            onClick={handleConnect}
            disabled={connecting || !url}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-success)] text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Plug className="w-4 h-4" />
            {connecting ? 'Connecting...' : 'Connect'}
          </button>
        )}

        {connected && (
          <span className="flex items-center gap-1.5 text-xs text-[var(--color-success)]">
            <span className="w-2 h-2 rounded-full bg-[var(--color-success)] animate-pulse" />
            Connected
          </span>
        )}
      </div>

      {error && (
        <div className="mt-2 text-xs text-[var(--color-danger)]">{error}</div>
      )}
    </div>
  );
}
