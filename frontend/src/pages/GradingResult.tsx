import React from 'react';
import { useLocation, Link, Navigate } from 'react-router-dom';
import { GradeResultData } from '../types';
import { GradeBadge } from '../components/GradeBadge';
import { ConfidenceBar } from '../components/ConfidenceBar';
import { ExplanationPanel } from '../components/ExplanationPanel';
import { ShieldAlert, ArrowLeft, RotateCcw } from 'lucide-react';

export const GradingResult: React.FC = () => {
  const location = useLocation();
  const result = location.state?.result as GradeResultData | undefined;

  if (!result) {
    return <Navigate to="/capture" replace />;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-20 md:pb-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
              Grading Result Output
            </span>
            <h2 className="text-2xl font-black text-civic-navy">System Evaluation</h2>
          </div>
          <GradeBadge grade={result.grade} size="lg" />
        </div>

        {/* Confidence Score Bar */}
        <ConfidenceBar confidence={result.confidence} />

        {/* Review Required Warning */}
        {result.review_required && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 space-y-1">
            <div className="flex items-center space-x-2 font-bold text-sm">
              <ShieldAlert className="w-5 h-5 text-amber-600" />
              <span>Human Senior Review Recommended</span>
            </div>
            <p className="text-xs text-amber-800">
              Confidence is below threshold or critical failure rules were flagged. Human expert has final decision authority.
            </p>
          </div>
        )}

        <hr className="border-slate-200" />

        {/* Explanation Panel */}
        <ExplanationPanel reasons={result.reasons} missingAttributes={result.missing_attributes} />

        {/* Actions */}
        <div className="pt-4 flex flex-col sm:flex-row gap-3">
          <Link
            to="/capture"
            className="flex-1 h-12 bg-civic-teal text-white font-bold text-sm rounded-xl flex items-center justify-center space-x-2 hover:bg-civic-lightTeal transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Grade Another Livestock</span>
          </Link>
          <Link
            to="/history"
            className="h-12 px-5 bg-slate-100 text-slate-700 font-bold text-sm rounded-xl flex items-center justify-center space-x-2 hover:bg-slate-200 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to History</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
