import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getGradingHistory } from '../services/historyService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { GradeBadge } from '../components/GradeBadge';
import { Search, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const GradingHistory: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['history'],
    queryFn: () => getGradingHistory(0, 50),
  });

  if (isLoading) return <LoadingSpinner message="Fetching grading history..." />;
  if (isError) return <ErrorState message={error instanceof Error ? error.message : 'Error'} onRetry={refetch} />;

  const events = data?.events || [];
  const filteredEvents = events.filter((e) =>
    e.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-20 md:pb-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-civic-navy">Grading Event History</h2>
            <p className="text-sm text-slate-500">Audit trail of all recorded health grading decisions.</p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-civic-teal focus:outline-none"
            />
          </div>
        </div>

        {filteredEvents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-bold text-slate-400 uppercase tracking-wider bg-slate-50">
                  <th className="p-3">Event ID</th>
                  <th className="p-3">AI Grade</th>
                  <th className="p-3">Human Grade</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {filteredEvents.map((e) => {
                  const hasDisagreement = e.human_grade && e.human_grade !== e.ai_grade;

                  return (
                    <tr key={e.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="p-3 font-mono text-xs text-slate-500">{e.id.substring(0, 13)}...</td>
                      <td className="p-3">
                        <GradeBadge grade={e.ai_grade} size="sm" />
                      </td>
                      <td className="p-3">
                        {e.human_grade ? (
                          <GradeBadge grade={e.human_grade} size="sm" />
                        ) : (
                          <span className="text-xs text-slate-400 italic">Not Provided</span>
                        )}
                      </td>
                      <td className="p-3 font-bold text-civic-navy">{e.confidence_score}%</td>
                      <td className="p-3">
                        {hasDisagreement ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                            <AlertTriangle className="w-3 h-3 mr-1" /> Disagreement
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                            <CheckCircle2 className="w-3 h-3 mr-1" /> Verified
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="No History Found"
            description="No grading events match your search query."
          />
        )}
      </div>
    </div>
  );
};
