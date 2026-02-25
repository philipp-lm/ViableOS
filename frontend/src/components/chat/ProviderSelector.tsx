import { KeyRound } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

const PROVIDERS: Record<string, { label: string; models: string[] }> = {
  anthropic: {
    label: 'Anthropic',
    models: ['claude-sonnet-4-6', 'claude-haiku-4-5', 'claude-opus-4-6', 'claude-opus-4-5'],
  },
  openai: {
    label: 'OpenAI',
    models: ['gpt-5.2', 'gpt-5.1', 'gpt-5-mini', 'o3'],
  },
  google: {
    label: 'Google',
    models: ['gemini-3-pro', 'gemini-3-flash', 'gemini-2.5-pro', 'gemini-2.5-flash'],
  },
  deepseek: {
    label: 'DeepSeek',
    models: ['deepseek-v3.2'],
  },
  xai: {
    label: 'xAI',
    models: ['grok-4'],
  },
  ollama: {
    label: 'Ollama (local)',
    models: ['llama-4', 'mistral-large', 'deepseek-v3'],
  },
};

export function ProviderSelector() {
  const { provider, model, apiKey, setProvider, setModel, setApiKey } = useChatStore();
  const currentProvider = PROVIDERS[provider] || PROVIDERS.anthropic;

  const handleProviderChange = (newProvider: string) => {
    setProvider(newProvider);
    const models = PROVIDERS[newProvider]?.models || [];
    if (models.length > 0) setModel(models[0]);
  };

  return (
    <div className="flex items-center gap-3 p-3 border-b border-[var(--color-border)]">
      <select
        value={provider}
        onChange={(e) => handleProviderChange(e.target.value)}
        className="bg-[var(--color-card)] text-[var(--color-text)] text-sm rounded-lg px-3 py-1.5 border border-[var(--color-border)] outline-none focus:border-[var(--color-primary)]"
      >
        {Object.entries(PROVIDERS).map(([key, p]) => (
          <option key={key} value={key}>{p.label}</option>
        ))}
      </select>

      <select
        value={model}
        onChange={(e) => setModel(e.target.value)}
        className="bg-[var(--color-card)] text-[var(--color-text)] text-sm rounded-lg px-3 py-1.5 border border-[var(--color-border)] outline-none focus:border-[var(--color-primary)]"
      >
        {currentProvider.models.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>

      {provider !== 'ollama' && (
        <div className="flex items-center gap-2 flex-1">
          <KeyRound className="w-4 h-4 text-[var(--color-muted)]" />
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="API Key (stored in-memory only)"
            className="flex-1 bg-[var(--color-card)] text-[var(--color-text)] text-sm rounded-lg px-3 py-1.5 border border-[var(--color-border)] outline-none focus:border-[var(--color-primary)] placeholder:text-[var(--color-muted)]"
          />
        </div>
      )}
    </div>
  );
}
