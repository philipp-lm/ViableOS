import { CheckCircle, Wand2 } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { useConfigStore } from '../../store/useConfigStore';
import type { AssessmentConfig, Config } from '../../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function transformAssessment(assessment: AssessmentConfig): Promise<Config> {
  const res = await fetch(`${API_BASE}/assessment/transform`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessment),
  });
  if (!res.ok) throw new Error(`Transform failed: ${res.status}`);
  return res.json();
}

export function AssessmentPreview() {
  const { sessionId, assessmentData, setAssessmentData } = useChatStore();
  const { setConfig, setView, setWizardStep } = useConfigStore();

  const handleFinalize = async () => {
    if (!sessionId) return;
    try {
      const res = await fetch(`${API_BASE}/chat/finalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await res.json();
      if (data.success && data.assessment) {
        setAssessmentData(data.assessment);
      }
    } catch {
      // ignore
    }
  };

  const handleUseInWizard = async () => {
    if (!assessmentData) return;
    try {
      const config = await transformAssessment(assessmentData);
      setConfig(config);
      setView('wizard');
      setWizardStep(0);
    } catch {
      // ignore
    }
  };

  if (!sessionId) return null;

  if (!assessmentData) {
    return (
      <div className="p-3 border-t border-[var(--color-border)]">
        <button
          onClick={handleFinalize}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
        >
          <CheckCircle className="w-4 h-4" />
          Finalize Assessment
        </button>
        <p className="text-xs text-[var(--color-muted)] mt-2 text-center">
          Ask the AI to generate the assessment JSON first, then click to extract it.
        </p>
      </div>
    );
  }

  const units = (() => {
    const levels = assessmentData.recursion_levels as Record<string, { operational_units?: unknown[] }> | undefined;
    const level0 = levels?.level_0;
    return level0?.operational_units?.length || 0;
  })();

  return (
    <div className="p-3 border-t border-[var(--color-border)] space-y-3">
      <div className="bg-[var(--color-bg)] rounded-lg p-3 space-y-2">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-[var(--color-success)]" />
          <span className="text-sm font-semibold text-[var(--color-text)]">Assessment Ready</span>
        </div>
        <div className="text-xs text-[var(--color-muted)] space-y-1">
          <div><strong>System:</strong> {assessmentData.system_name}</div>
          <div><strong>Purpose:</strong> {assessmentData.purpose?.slice(0, 80)}...</div>
          <div><strong>Units:</strong> {units}</div>
          {assessmentData.success_criteria && (
            <div><strong>Success criteria:</strong> {assessmentData.success_criteria.length}</div>
          )}
        </div>
      </div>
      <button
        onClick={handleUseInWizard}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
      >
        <Wand2 className="w-4 h-4" />
        Use in Wizard
      </button>
    </div>
  );
}
