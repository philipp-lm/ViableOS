import { Bot, User } from 'lucide-react';
import type { ChatMessage } from '../../types';

interface Props {
  message: ChatMessage;
  isStreaming?: boolean;
}

function renderMarkdown(text: string) {
  // Simple markdown rendering: bold, italic, code blocks, inline code, lists, headers
  const lines = text.split('\n');
  const elements: (string | JSX.Element)[] = [];
  let inCodeBlock = false;
  let codeBlockContent: string[] = [];
  let codeBlockLang = '';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith('```')) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeBlockLang = line.slice(3).trim();
        codeBlockContent = [];
        continue;
      } else {
        inCodeBlock = false;
        elements.push(
          <pre key={`code-${i}`} className="bg-[var(--color-bg)] rounded-lg p-3 my-2 overflow-x-auto text-xs">
            <code>{codeBlockContent.join('\n')}</code>
          </pre>
        );
        continue;
      }
    }

    if (inCodeBlock) {
      codeBlockContent.push(line);
      continue;
    }

    if (line.startsWith('### ')) {
      elements.push(<h4 key={i} className="font-semibold text-sm mt-3 mb-1">{formatInline(line.slice(4))}</h4>);
    } else if (line.startsWith('## ')) {
      elements.push(<h3 key={i} className="font-bold text-sm mt-3 mb-1">{formatInline(line.slice(3))}</h3>);
    } else if (line.startsWith('# ')) {
      elements.push(<h2 key={i} className="font-bold mt-3 mb-1">{formatInline(line.slice(2))}</h2>);
    } else if (/^\d+\.\s/.test(line)) {
      elements.push(<div key={i} className="ml-4 my-0.5">{formatInline(line)}</div>);
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      elements.push(<div key={i} className="ml-4 my-0.5">{formatInline(line)}</div>);
    } else if (line.trim() === '') {
      elements.push(<div key={i} className="h-2" />);
    } else {
      elements.push(<p key={i} className="my-0.5">{formatInline(line)}</p>);
    }
  }

  return <>{elements}</>;
}

function formatInline(text: string): string | JSX.Element {
  // Replace **bold**, *italic*, `code`
  const parts: (string | JSX.Element)[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Bold
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
    // Inline code
    const codeMatch = remaining.match(/`([^`]+)`/);

    let firstMatch: { index: number; length: number; element: JSX.Element; raw: string } | null = null;

    if (boldMatch && boldMatch.index !== undefined) {
      const candidate = {
        index: boldMatch.index,
        length: boldMatch[0].length,
        element: <strong key={key++}>{boldMatch[1]}</strong>,
        raw: boldMatch[0],
      };
      if (!firstMatch || candidate.index < firstMatch.index) firstMatch = candidate;
    }

    if (codeMatch && codeMatch.index !== undefined) {
      const candidate = {
        index: codeMatch.index,
        length: codeMatch[0].length,
        element: <code key={key++} className="bg-[var(--color-bg)] px-1 py-0.5 rounded text-xs">{codeMatch[1]}</code>,
        raw: codeMatch[0],
      };
      if (!firstMatch || candidate.index < firstMatch.index) firstMatch = candidate;
    }

    if (firstMatch) {
      if (firstMatch.index > 0) {
        parts.push(remaining.slice(0, firstMatch.index));
      }
      parts.push(firstMatch.element);
      remaining = remaining.slice(firstMatch.index + firstMatch.length);
    } else {
      parts.push(remaining);
      break;
    }
  }

  if (parts.length === 1 && typeof parts[0] === 'string') return parts[0];
  return <>{parts}</>;
}

export function MessageBubble({ message, isStreaming }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser
            ? 'bg-[var(--color-primary)]'
            : 'bg-[var(--color-secondary)]'
        }`}
      >
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-[var(--color-primary)] text-white'
            : 'bg-[var(--color-card)] text-[var(--color-text)] border border-[var(--color-border)]'
        }`}
      >
        {isUser ? message.content : renderMarkdown(message.content)}
        {isStreaming && !isUser && (
          <span className="inline-block w-2 h-4 ml-1 bg-[var(--color-primary)] animate-pulse rounded-sm" />
        )}
      </div>
    </div>
  );
}
