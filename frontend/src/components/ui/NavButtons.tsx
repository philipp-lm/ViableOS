import { ArrowLeft, ArrowRight } from 'lucide-react';

interface Props {
  onBack?: () => void;
  onNext?: () => void;
  nextLabel?: string;
  nextDisabled?: boolean;
}

export function NavButtons({ onBack, onNext, nextLabel = 'Next', nextDisabled }: Props) {
  return (
    <div className="flex justify-between mt-10 pt-6 border-t border-[var(--color-border)]">
      {onBack ? (
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-muted)] hover:text-[var(--color-text)] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
      ) : (
        <div />
      )}
      {onNext && (
        <button
          type="button"
          onClick={onNext}
          disabled={nextDisabled}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-medium rounded-lg bg-[var(--color-primary)] text-white hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {nextLabel} <ArrowRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
