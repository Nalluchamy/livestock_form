import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  suggestion: string;
  icon: LucideIcon;
  statusColor: 'green' | 'amber' | 'red';
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  suggestion,
  icon: Icon,
  statusColor,
}) => {
  const colorStyles = {
    green: 'border-l-4 border-l-emerald-500 bg-emerald-50/50 text-emerald-900',
    amber: 'border-l-4 border-l-amber-500 bg-amber-50/50 text-amber-900',
    red: 'border-l-4 border-l-rose-500 bg-rose-50/50 text-rose-900',
  };

  const iconStyles = {
    green: 'bg-emerald-100 text-emerald-600',
    amber: 'bg-amber-100 text-amber-600',
    red: 'bg-rose-100 text-rose-600',
  };

  return (
    <div className={`p-4 rounded-xl shadow-sm border border-slate-200 bg-white ${colorStyles[statusColor]} space-y-3`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-600">{title}</span>
        <div className={`p-2 rounded-lg ${iconStyles[statusColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="text-3xl font-extrabold tracking-tight text-civic-navy">{value}</div>
      <p className="text-xs text-slate-600 border-t border-slate-200/80 pt-2 font-medium">{suggestion}</p>
    </div>
  );
};
