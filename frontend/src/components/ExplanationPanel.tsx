import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info } from 'lucide-react';

interface ExplanationPanelProps {
  reasons: string[];
  missingAttributes: string[];
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  reasons,
  missingAttributes,
}) => {
  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-civic-navy flex items-center">
        <Info className="w-5 h-5 mr-2 text-civic-teal" /> Explainable Decision Factors
      </h3>

      {reasons.length > 0 ? (
        <div className="space-y-2">
          {reasons.map((reason, idx) => {
            const isCritical = reason.startsWith('Critical Failure');
            const isWarning = reason.startsWith('Warning');

            return (
              <div
                key={idx}
                className={`p-3 rounded-lg flex items-start space-x-3 text-sm font-medium border ${
                  isCritical
                    ? 'bg-rose-50 border-rose-200 text-rose-800'
                    : isWarning
                    ? 'bg-amber-50 border-amber-200 text-amber-800'
                    : 'bg-emerald-50 border-emerald-200 text-emerald-800'
                }`}
              >
                {isCritical ? (
                  <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
                ) : isWarning ? (
                  <AlertTriangle className="w-5 h-5 shrink-0 text-amber-600 mt-0.5" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600 mt-0.5" />
                )}
                <span>{reason}</span>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-slate-500 italic">No specific rule reasons generated.</p>
      )}

      {missingAttributes.length > 0 && (
        <div className="p-3 bg-slate-100 border border-slate-200 rounded-lg space-y-1">
          <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
            Missing Observations
          </span>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {missingAttributes.map((attr) => (
              <span
                key={attr}
                className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-200 text-slate-700"
              >
                {attr.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
