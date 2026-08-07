import React from 'react';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';

interface SyncStatusBadgeProps {
  isOnline: boolean;
  pendingCount: number;
  isSyncing?: boolean;
}

export const SyncStatusBadge: React.FC<SyncStatusBadgeProps> = ({
  isOnline,
  pendingCount,
  isSyncing,
}) => {
  if (isSyncing) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
        <RefreshCw className="w-3.5 h-3.5 mr-1 animate-spin" /> Syncing Queue...
      </span>
    );
  }

  if (!isOnline) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
        <WifiOff className="w-3.5 h-3.5 mr-1" /> Offline ({pendingCount} Queued)
      </span>
    );
  }

  if (pendingCount > 0) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
        <RefreshCw className="w-3.5 h-3.5 mr-1" /> {pendingCount} Pending Sync
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
      <Wifi className="w-3.5 h-3.5 mr-1" /> Online & Synced
    </span>
  );
};
