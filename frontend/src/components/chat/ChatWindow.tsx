import { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { MessageBubble } from './MessageBubble';
import type { ChatMessage } from '../../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function ChatWindow() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const {
    sessionId, provider, model, apiKey, messages, isStreaming, error,
    setSessionId, setIsStreaming, setError, addMessage, appendToLastMessage,
  } = useChatStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startSession = async () => {
    const res = await fetch(`${API_BASE}/chat/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, model, api_key: apiKey }),
    });
    if (!res.ok) throw new Error(`Failed to start session: ${res.status}`);
    const data = await res.json();
    setSessionId(data.session_id);
    return data.session_id;
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isStreaming) return;
    if (!apiKey && provider !== 'ollama') {
      setError('Please enter your API key first.');
      return;
    }

    setInput('');
    setError(null);
    setIsStreaming(true);

    try {
      let sid = sessionId;
      if (!sid) {
        sid = await startSession();
      }

      const userMsg: ChatMessage = {
        role: 'user',
        content: text,
        timestamp: Date.now() / 1000,
      };
      addMessage(userMsg);

      // Add empty assistant message for streaming
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: '',
        timestamp: Date.now() / 1000,
      };
      addMessage(assistantMsg);

      // SSE streaming via fetch + ReadableStream
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid, message: text }),
      });

      if (!res.ok) {
        throw new Error(`Chat request failed: ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            if (data.startsWith('[ERROR]')) {
              setError(data);
              continue;
            }
            appendToLastMessage(data);
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-3">
            <div className="text-4xl">🧠</div>
            <h2 className="text-lg font-semibold text-[var(--color-text)]">VSM Expert Chat</h2>
            <p className="text-sm text-[var(--color-muted)] max-w-md">
              I'll interview you about your business and create a structured assessment
              that maps your operations onto the Viable System Model. Start by telling me
              about your organization.
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'assistant'}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mb-2 px-3 py-2 text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 rounded-lg border border-[var(--color-danger)]/20">
          {error}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-[var(--color-border)]">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your business or organization..."
            rows={1}
            className="flex-1 bg-[var(--color-card)] text-[var(--color-text)] text-sm rounded-xl px-4 py-3 border border-[var(--color-border)] outline-none focus:border-[var(--color-primary)] placeholder:text-[var(--color-muted)] resize-none"
            style={{ minHeight: '44px', maxHeight: '120px' }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = '44px';
              target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
            }}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            className="px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
