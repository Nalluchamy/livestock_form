import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, History, ShieldCheck, ArrowRight, Activity, AlertTriangle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getMetrics } from '../services/metricsService';
import { getGradingHistory } from '../services/historyService';
import { GradeBadge } from '../components/GradeBadge';

export const Home: React.FC = () => {
  const { data: metrics } = useQuery({ queryKey: ['metrics'], queryFn: getMetrics });
  const { data: history } = useQuery({
    queryKey: ['recentHistory'],
    queryFn: () => getGradingHistory(0, 3),
  });

  return (
    <div className="space-y-6 pb-20 md:pb-6">
      {/* Hero Card */}
      <div className="bg-gradient-to-r from-civic-navy to-civic-slate text-white p-6 rounded-2xl shadow-md border border-slate-800 space-y-4">
        <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-civic-teal/30 text-civic-lightTeal border border-civic-teal/40">
          <Activity className="w-3.5 h-3.5 mr-1.5" /> Explainable AI Hackathon Prototype
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Explainable Livestock Health Grading System
        </h2>
        <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
          AI-assisted health grading that reduces human disagreement by providing deterministic, transparent, and explainable decision factors. Human reviewers always maintain final authority.
        </p>

        <div className="pt-2 flex flex-col sm:flex-row gap-3">
          <Link
            to="/capture"
            className="h-12 px-5 bg-civic-teal hover:bg-civic-lightTeal text-white font-bold text-sm rounded-xl flex items-center justify-center space-x-2 shadow-lg transition-transform active:scale-[0.98]"
          >
            <Camera className="w-5 h-5" />
            <span>Capture New Grade</span>
          </Link>
          <Link
            to="/ethics"
            className="h-12 px-5 bg-white/10 hover:bg-white/20 text-white font-semibold text-sm rounded-xl flex items-center justify-center space-x-2 border border-white/20 transition-colors"
          >
            <ShieldCheck className="w-5 h-5 text-civic-lightTeal" />
            <span>Ethical Guardrails</span>
          </Link>
        </div>
      </div>

      {/* Quick Metrics Bar */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-400 uppercase">Total Gradings</span>
            <div className="text-2xl font-black text-civic-navy">{metrics.total_gradings}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-400 uppercase">Agreement Rate</span>
            <div className="text-2xl font-black text-emerald-600">{metrics.agreement_rate}%</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-400 uppercase">Avg Confidence</span>
            <div className="text-2xl font-black text-civic-teal">{metrics.average_confidence}%</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-400 uppercase">Pending Reviews</span>
            <div className="text-2xl font-black text-amber-600">{metrics.pending_reviews}</div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-civic-navy flex items-center">
            <History className="w-5 h-5 mr-2 text-civic-teal" /> Recent Grading Events
          </h3>
          <Link to="/history" className="text-xs font-bold text-civic-teal hover:underline flex items-center">
            View All <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        {history && history.events.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {history.events.map((e) => (
              <div key={e.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <GradeBadge grade={e.ai_grade} size="sm" />
                  <div>
                    <span className="text-xs font-semibold text-slate-400 block">
                      ID: {e.id.substring(0, 8)}...
                    </span>
                    <span className="text-xs font-medium text-slate-600">
                      Confidence: {e.confidence_score}%
                    </span>
                  </div>
                </div>
                <div>
                  {e.human_grade && e.human_grade !== e.ai_grade ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800">
                      <AlertTriangle className="w-3 h-3 mr-1" /> Disagreement
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800">
                      Agreed
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500 italic">No grading events recorded yet. Start by capturing one above!</p>
        )}
      </div>
    </div>
  );
};
