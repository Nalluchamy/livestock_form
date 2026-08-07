import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

interface ConflictDialogProps {
  isOpen: boolean;
  onResolve: (strategy: 'server' | 'local') => void;
}

export const ConflictDialog: React.FC<ConflictDialogProps> = ({ isOpen, onResolve }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
        <div className="flex items-center space-x-3 text-amber-600">
          <AlertTriangle className="w-7 h-7 shrink-0" />
          <h3 className="text-lg font-bold text-civic-navy">Offline Sync Collision Detected</h3>
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          This sample was graded remotely while your device was offline. Please select which record to preserve:
        </p>

        <div className="space-y-2 pt-2">
          <button
            onClick={() => onResolve('server')}
            className="w-full p-3 bg-slate-100 hover:bg-slate-200 rounded-xl text-left border border-slate-300 flex items-center justify-between"
          >
            <div>
              <span className="font-bold text-sm text-civic-navy block">Keep Server Version (Recommended)</span>
              <span className="text-xs text-slate-500">Preserves verified remote database state</span>
            </div>
            <ShieldCheck className="w-5 h-5 text-civic-teal" />
          </button>

          <button
            onClick={() => onResolve('local')}
            className="w-full p-3 bg-amber-50 hover:bg-amber-100 rounded-xl text-left border border-amber-200 flex items-center justify-between"
          >
            <div>
              <span className="font-bold text-sm text-amber-900 block">Overwrite with Local Field Version</span>
              <span className="text-xs text-amber-700">Pushes your offline field observations</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};
