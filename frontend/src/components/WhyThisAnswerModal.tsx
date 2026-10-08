import React from 'react';
import { WhyThisAnswerPayload } from '../lib/types';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle, Search, Layers } from 'lucide-react';

interface WhyThisAnswerModalProps {
  payload: WhyThisAnswerPayload | null;
  onClose: () => void;
}

export const WhyThisAnswerModal: React.FC<WhyThisAnswerModalProps> = ({ payload, onClose }) => {
  if (!payload) return null;

  const levelColor =
    payload.evidence_level === 'HIGH'
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
      : payload.evidence_level === 'MEDIUM'
      ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
      : 'bg-red-500/20 text-red-400 border-red-500/40';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full bg-slate-800 p-2 text-slate-400 hover:bg-slate-700 hover:text-white"
        >
          ✕
        </button>

        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <ShieldCheck className="h-7 w-7 text-blue-400" />
          <div>
            <h2 className="text-xl font-bold text-white">Why This Answer?</h2>
            <p className="text-xs text-slate-400">Active Visual Verification Engine Audit Trail</p>
          </div>
        </div>

        {/* Evidence Score Level */}
        <div className="mt-5 flex items-center justify-between rounded-xl border bg-slate-800/40 p-4">
          <div>
            <span className="text-xs uppercase tracking-wider text-slate-400">Evidence Level</span>
            <div className="mt-1 flex items-center gap-2">
              <span className={`inline-block rounded-lg border px-3 py-1 text-sm font-bold ${levelColor}`}>
                {payload.evidence_level} EVIDENCE
              </span>
              <span className="text-xs text-slate-400">(Calculated at runtime from actual pixels)</span>
            </div>
          </div>
        </div>

        {/* Answer Summary */}
        <div className="mt-4 rounded-xl bg-slate-800/60 p-4 border border-slate-700/50">
          <span className="text-xs text-slate-400 font-semibold uppercase">Verified Answer</span>
          <p className="mt-1 text-sm font-medium text-slate-100">{payload.answer}</p>
        </div>

        {/* Verification State Machine Steps */}
        <div className="mt-5">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-300">
            <Search className="h-4 w-4 text-blue-400" />
            Active Verification Pipeline Steps
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {payload.verification_steps.map((step, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-200"
              >
                <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                <span className="font-mono">{step}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Unsupported Claims (Hallucination Rejections) */}
        {payload.unsupported_claims && payload.unsupported_claims.length > 0 && (
          <div className="mt-5 rounded-xl border border-red-500/40 bg-red-950/30 p-4">
            <div className="flex items-center gap-2 text-red-400">
              <AlertTriangle className="h-5 w-5" />
              <h4 className="font-semibold text-sm">AI Refused Unsupported Claim</h4>
            </div>
            <ul className="mt-2 space-y-1 pl-7 text-xs text-red-300 list-disc">
              {payload.unsupported_claims.map((claim, idx) => (
                <li key={idx}>{claim}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Grounding Annotations */}
        <div className="mt-5">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-300">
            <Layers className="h-4 w-4 text-blue-400" />
            Verified Visual Grounding Evidence ({payload.annotations.length} Objects)
          </h4>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {payload.annotations.map((ann, idx) => (
              <div key={idx} className="rounded-lg bg-slate-800/60 p-2.5 text-xs border border-slate-700/50">
                <div className="font-medium text-slate-200 capitalize">{ann.label}</div>
                <div className="text-slate-400 mt-0.5">Confidence: {Math.round(ann.confidence * 100)}%</div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-xl bg-slate-800 px-5 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700"
          >
            Close Audit Trail
          </button>
        </div>
      </div>
    </div>
  );
};
