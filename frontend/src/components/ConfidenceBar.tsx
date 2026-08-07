import React from 'react';

interface ConfidenceBarProps {
  confidence: number;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ confidence }) => {
  const getBarColor = (val: number) => {
    if (val >= 80) return 'bg-emerald-500';
    if (val >= 60) return 'bg-teal-500';
    if (val >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="w-full space-y-1.5">
      <div className="flex justify-between items-center text-sm font-semibold text-slate-700">
        <span>Confidence Score</span>
        <span className="font-bold text-civic-navy">{confidence}%</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden p-0.5 border border-slate-300">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${getBarColor(confidence)}`}
          style={{ width: `${Math.min(100, Math.max(0, confidence))}%` }}
        />
      </div>
    </div>
  );
};
