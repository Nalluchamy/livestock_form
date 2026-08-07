import React from 'react';

interface ConnectionIndicatorProps {
  isOnline: boolean;
}

export const ConnectionIndicator: React.FC<ConnectionIndicatorProps> = ({ isOnline }) => {
  return (
    <div className="flex items-center space-x-1.5 text-xs font-semibold">
      <span
        className={`w-2.5 h-2.5 rounded-full ${
          isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
        }`}
      />
      <span className="text-slate-300 hidden sm:inline">{isOnline ? 'Online' : 'Offline'}</span>
    </div>
  );
};
