import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  active?: boolean;
}

export function Card({ children, className = '', onClick, active }: Props) {
  return (
    <div
      onClick={onClick}
      className={`rounded-xl border p-4 transition-all ${
        onClick ? 'cursor-pointer hover:border-[var(--color-primary)]' : ''
      } ${
        active
          ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
          : 'border-[var(--color-border)] bg-[var(--color-card)]'
      } ${className}`}
    >
      {children}
    </div>
  );
}
