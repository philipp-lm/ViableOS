import { useConfigStore } from '../store/useConfigStore';
import { TemplateStep } from '../components/wizard/TemplateStep';
import { IdentityStep } from '../components/wizard/IdentityStep';
import { UnitsStep } from '../components/wizard/UnitsStep';
import { BudgetStep } from '../components/wizard/BudgetStep';
import { HitlStep } from '../components/wizard/HitlStep';
import { ReviewStep } from '../components/wizard/ReviewStep';
import { AnimatePresence, motion } from 'framer-motion';

const STEPS = [TemplateStep, IdentityStep, UnitsStep, BudgetStep, HitlStep, ReviewStep];

export function WizardPage() {
  const step = useConfigStore((s) => s.wizardStep);
  const StepComponent = STEPS[step] ?? TemplateStep;

  return (
    <div className="max-w-3xl mx-auto">
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
