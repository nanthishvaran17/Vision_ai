import React from 'react';
import { CheckCircle2, Loader2, Search } from 'lucide-react';

interface VerificationStep {
  name: string;
  status: 'pending' | 'active' | 'completed';
}

interface LiveVerificationProgressProps {
  steps: VerificationStep[];
  currentStatusText?: string;
}

export const LiveVerificationProgress: React.FC<LiveVerificationProgressProps> = ({
  steps,
  currentStatusText
}) => {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="my-3 rounded-xl border border-blue-500/30 bg-slate-900/90 p-4 shadow-lg backdrop-blur-md animate-in fade-in duration-300">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
        <Search className="h-4 w-4 animate-pulse" />
        Live Active Verification Engine
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center gap-1.5">
            {step.status === 'completed' ? (
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="h-3.5 w-3.5" />
                ✓ {step.name}
              </span>
            ) : step.status === 'active' ? (
              <span className="flex items-center gap-1 text-blue-400 font-semibold animate-pulse">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ⟳ {step.name}
              </span>
            ) : (
              <span className="text-slate-500">
                • {step.name}
              </span>
            )}
          </div>
        ))}
      </div>

      {currentStatusText && (
        <div className="mt-2 text-xs font-mono text-slate-300">
          {currentStatusText}
        </div>
      )}
    </div>
  );
};
