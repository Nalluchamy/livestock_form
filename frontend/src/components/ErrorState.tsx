import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-rose-50 rounded-2xl border border-rose-200 shadow-sm my-6 space-y-3">
      <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-rose-600">
        <AlertOctagon className="w-6 h-6" />
      </div>
      <h4 className="text-base font-bold text-rose-900">An Error Occurred</h4>
      <p className="text-sm text-rose-700 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-4 py-2 bg-rose-600 text-white font-semibold text-sm rounded-lg hover:bg-rose-700 transition-colors flex items-center space-x-1.5"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
};
