import { Download, Package } from 'lucide-react';
import { useState } from 'react';
import { api } from '../../api/client';
import { useConfigStore } from '../../store/useConfigStore';
import type { Config } from '../../types';

interface Props {
  config: Config;
}

export function ExportPanel({ config }: Props) {
  const [generating, setGenerating] = useState(false);
  const [done, setDone] = useState(false);
  const { runtimeTarget, setRuntimeTarget } = useConfigStore();

  const downloadYaml = () => {
    const yamlStr = JSON.stringify(config, null, 2);
    const blob = new Blob([yamlStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'viableos.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const generatePackage = async () => {
    setGenerating(true);
    setDone(false);
    try {
      const blob = runtimeTarget === 'langgraph'
        ? await api.generateLanggraphPackage(config)
        : await api.generatePackage(config);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = runtimeTarget === 'langgraph'
        ? 'viableos-langgraph.zip'
        : 'viableos-openclaw.zip';
      a.click();
      URL.revokeObjectURL(url);
      setDone(true);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Export</h3>

      <div className="flex items-center gap-3 mb-4">
        <span className="text-sm text-[var(--color-muted)]">Runtime:</span>
        <div className="flex rounded-lg border border-[var(--color-border)] overflow-hidden">
          <button
            onClick={() => setRuntimeTarget('openclaw')}
            className={`px-4 py-1.5 text-sm transition-all ${
              runtimeTarget === 'openclaw'
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-transparent text-[var(--color-muted)] hover:text-[var(--color-text)]'
            }`}
          >
            OpenClaw
          </button>
          <button
            onClick={() => setRuntimeTarget('langgraph')}
            className={`px-4 py-1.5 text-sm transition-all ${
              runtimeTarget === 'langgraph'
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-transparent text-[var(--color-muted)] hover:text-[var(--color-text)]'
            }`}
          >
            LangGraph
          </button>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={downloadYaml}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-[var(--color-border)] text-sm text-[var(--color-muted)] hover:border-[var(--color-primary)] hover:text-[var(--color-text)] transition-all"
        >
          <Download className="w-4 h-4" /> Download Config (JSON)
        </button>
        <button
          onClick={generatePackage}
          disabled={generating}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[var(--color-primary)] text-sm text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
        >
          <Package className="w-4 h-4" />
          {generating
            ? 'Generating...'
            : `Generate ${runtimeTarget === 'langgraph' ? 'LangGraph' : 'OpenClaw'} Package`}
        </button>
      </div>
      {done && (
        <div className="mt-3 text-sm text-[var(--color-success)]">
          {runtimeTarget === 'langgraph'
            ? 'LangGraph package generated. Contains graph.py, state.py, agent prompts, and langgraph.json.'
            : 'OpenClaw package generated. Each agent includes SOUL.md, SKILL.md, HEARTBEAT.md, USER.md, MEMORY.md, and AGENTS.md.'}
        </div>
      )}
    </div>
  );
}
