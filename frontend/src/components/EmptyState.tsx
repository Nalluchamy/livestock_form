import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white rounded-2xl border border-slate-200 shadow-sm my-6 space-y-3">
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
        <Inbox className="w-6 h-6" />
      </div>
      <h4 className="text-base font-bold text-civic-navy">{title}</h4>
      <p className="text-sm text-slate-500 max-w-sm">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 bg-civic-teal text-white font-semibold text-sm rounded-lg hover:bg-civic-lightTeal transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
