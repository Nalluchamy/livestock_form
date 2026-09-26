import React from 'react';
import { Outlet } from 'react-router-dom';
import { AppHeader } from '../components/AppHeader';
import { Sidebar } from '../components/Sidebar';
import { BottomNavigation } from '../components/BottomNavigation';
import { OfflineBanner } from '../components/OfflineBanner';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

export const RootLayout: React.FC = () => {
  const isOnline = useNetworkStatus();

  return (
    <div className="min-h-screen bg-civic-bg flex flex-col">
      <OfflineBanner isOnline={isOnline} />
      <AppHeader />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 md:ml-64 p-4 sm:p-6 max-w-7xl mx-auto w-full">
          <ErrorBoundary
            title="Page View Error"
            subTitle="This specific section encountered an unexpected rendering fault. You can refresh this view or navigate to other sections."
          >
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <BottomNavigation />
    </div>
  );
};
