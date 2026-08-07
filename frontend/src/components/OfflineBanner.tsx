import React from 'react';
import { WifiOff } from 'lucide-react';

interface OfflineBannerProps {
  isOnline: boolean;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({ isOnline }) => {
  if (isOnline) return null;

  return (
    <div className="bg-amber-500 text-white px-4 py-2 text-xs font-bold flex items-center justify-center space-x-2 shadow-inner">
      <WifiOff className="w-4 h-4 shrink-0 animate-pulse" />
      <span>
        You are working offline. Grading decisions will save locally to IndexedDB and auto-sync when online.
      </span>
    </div>
  );
};
