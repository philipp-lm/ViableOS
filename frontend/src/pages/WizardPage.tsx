import { useConfigStore } from '../store/useConfigStore';
import { TemplateStep } from '../components/wizard/TemplateStep';
import { IdentityStep } from '../components/wizard/IdentityStep';
import { UnitsStep } from '../components/wizard/UnitsStep';
import { BudgetStep } from '../components/wizard/BudgetStep';
import { HitlStep } from '../components/wizard/HitlStep';
import { ReviewStep } from '../components/wizard/ReviewStep';
import { AnimatePresence, motion } from 'framer-motion';
import { Check, ChevronRight } from 'lucide-react';

const STEPS = [TemplateStep, IdentityStep, UnitsStep, BudgetStep, HitlStep, ReviewStep];
const STEP_LABELS = ['Template', 'Identity', 'Units', 'Budget', 'HITL', 'Review'];

export function WizardPage() {
  const { wizardStep: step, setWizardStep, config, templateKey } = useConfigStore();
  const StepComponent = STEPS[step] ?? TemplateStep;
  const vs = config.viable_system;

  const isStepComplete = (i: number): boolean => {
    if (i === 0) return !!templateKey;
    if (i === 1) return !!(vs.name && vs.identity?.purpose);
    if (i === 2) return vs.system_1.length > 0;
    if (i === 3) return !!(vs.budget?.monthly_usd);
    if (i === 4) return !!(vs.human_in_the_loop?.notification_channel);
    if (i === 5) return false; // review is never "complete" in this sense
    return false;
  };

  const isPreFilled = templateKey === 'assessment';

  return (
    <div className="max-w-3xl mx-auto">
      {/* Step progress bar */}
      <div className="flex items-center gap-1 mb-6">
        {STEP_LABELS.map((label, i) => {
          const completed = isStepComplete(i);
          const active = i === step;
          return (
            <button
              key={i}
              onClick={() => setWizardStep(i)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                active
                  ? 'bg-[var(--color-primary)] text-white'
                  : completed
                  ? 'bg-[var(--color-success)]/15 text-[var(--color-success)] hover:bg-[var(--color-success)]/25'
                  : 'text-[var(--color-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-card)]'
              }`}
            >
              {completed && !active ? (
                <Check className="w-3 h-3" />
              ) : (
                <span className="w-4 text-center">{i + 1}</span>
              )}
              {label}
              {isPreFilled && i > 0 && i < 5 && completed && (
                <span className="text-[9px] uppercase bg-[var(--color-accent)]/20 text-[var(--color-accent)] px-1 rounded">
                  pre-filled
                </span>
              )}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          <StepComponent />
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
