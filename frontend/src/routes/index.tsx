import { createBrowserRouter } from 'react-router-dom';
import { RootLayout } from '../layouts/RootLayout';
import { Home } from '../pages/Home';
import { CaptureGrade } from '../pages/CaptureGrade';
import { GradingResult } from '../pages/GradingResult';
import { GradingHistory } from '../pages/GradingHistory';
import { DisagreementReview } from '../pages/DisagreementReview';
import { MetricsDashboard } from '../pages/MetricsDashboard';
import { EthicsLimitations } from '../pages/EthicsLimitations';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'capture', element: <CaptureGrade /> },
      { path: 'result', element: <GradingResult /> },
      { path: 'history', element: <GradingHistory /> },
      { path: 'disagreements', element: <DisagreementReview /> },
      { path: 'metrics', element: <MetricsDashboard /> },
      { path: 'ethics', element: <EthicsLimitations /> },
    ],
  },
]);
