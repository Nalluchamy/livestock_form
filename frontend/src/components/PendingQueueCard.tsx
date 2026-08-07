import React from 'react';
import { AlertOctagon, RefreshCw, Trash2 } from 'lucide-react';
import { QueuedGradingItem } from '../utils/localDatabase';

interface PendingQueueCardProps {
  items: QueuedGradingItem[];
  onSyncNow: () => void;
  onClearItem: (id: string) => void;
  isSyncing: boolean;
}

export const PendingQueueCard: React.FC<PendingQueueCardProps> = ({
  items,
  onSyncNow,
  onClearItem,
  isSyncing,
}) => {
  if (items.length === 0) return null;

  return (
    <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl space-y-3 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-5 h-5 text-amber-600" />
          <h4 className="font-bold text-amber-950 text-sm">
            {items.length} Offline Grading Event{items.length > 1 ? 's' : ''} Queued
          </h4>
        </div>
        <button
          onClick={onSyncNow}
          disabled={isSyncing}
          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-lg shadow-sm flex items-center space-x-1 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>{isSyncing ? 'Syncing...' : 'Sync Now'}</span>
        </button>
      </div>

      <div className="divide-y divide-amber-200/60 max-h-48 overflow-y-auto">
        {items.map((item) => (
          <div key={item.id} className="py-2 flex items-center justify-between text-xs font-medium text-amber-900">
            <div>
              <span className="font-mono block">BCS: {item.attributes.body_condition}</span>
              <span className="text-amber-700 font-normal">
                {new Date(item.timestamp).toLocaleTimeString()} - Status: {item.status}
              </span>
            </div>
            <button
              onClick={() => onClearItem(item.id)}
              className="text-amber-700 hover:text-rose-600 p-1"
              title="Remove queue item"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
