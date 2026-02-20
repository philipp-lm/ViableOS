import { Info } from 'lucide-react';
import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  title?: string;
}

export function InfoCallout({ children, title }: Props) {
  return (
    <div className="flex gap-3 p-3 rounded-lg bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/30 text-sm">
      <Info className="w-4 h-4 mt-0.5 text-[var(--color-primary)] shrink-0" />
      <div>
        {title && <div className="font-medium text-[var(--color-primary)] mb-0.5">{title}</div>}
        <div className="text-[var(--color-muted)]">{children}</div>
      </div>
    </div>
  );
}
