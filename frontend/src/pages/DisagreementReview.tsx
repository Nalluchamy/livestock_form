import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getReviews, createReview, resolveReview } from '../services/reviewService';
import { GradeLevel, ReviewStatus, ReviewItem } from '../types';
import { 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  Clock, 
  Filter, 
  UserCheck, 
  Lock,
  PlusCircle,
  XCircle,
  FileCheck
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';

export const DisagreementReview: React.FC = () => {
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [showLogModal, setShowLogModal] = useState<boolean>(false);
  const [selectedReviewForResolve, setSelectedReviewForResolve] = useState<ReviewItem | null>(null);

  // New Disagreement Form State
  const [humanGrade, setHumanGrade] = useState<GradeLevel>('B');
  const [systemGrade, setSystemGrade] = useState<GradeLevel>('C');
  const [reason, setReason] = useState<string>('Body condition score is borderline 2.0');

  // Resolution Form State
  const [reviewerId, setReviewerId] = useState<string>('SR-VET-01');
  const [reviewerAction, setReviewerAction] = useState<'UPHELD_HUMAN' | 'ACCEPTED_SYSTEM' | 'EXPERT_OVERRIDE'>('UPHELD_HUMAN');
  const [finalDecision, setFinalDecision] = useState<GradeLevel>('B');
  const [resolutionRationale, setResolutionRationale] = useState<string>('');

  // 1. Fetch persistent reviews
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['reviews', activeTab],
    queryFn: () => getReviews(activeTab === 'ALL' ? undefined : activeTab),
  });

  // 2. Create review mutation
  const createMutation = useMutation({
    mutationFn: createReview,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
      setShowLogModal(false);
      setReason('');
    },
  });

  // 3. Resolve review mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: any }) => resolveReview(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
      setSelectedReviewForResolve(null);
      setResolutionRationale('');
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      human_grade: humanGrade,
      system_grade: systemGrade,
      reason,
    });
  };

  const handleResolveSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReviewForResolve) return;

    resolveMutation.mutate({
      id: selectedReviewForResolve.id,
      payload: {
        reviewer_id: reviewerId,
        reviewer_action: reviewerAction,
        reviewer_final_decision: finalDecision,
        reviewer_rationale: resolutionRationale || `Authoritative resolution by ${reviewerId}.`,
      }
    });
  };

  if (isLoading) return <LoadingSpinner message="Loading persistent disagreement review queue..." />;
  if (isError) return <ErrorState message={error instanceof Error ? error.message : 'Failed to fetch reviews'} onRetry={refetch} />;

  const reviews = data?.reviews || [];
  const stats = data?.stats;

  const statusBadge = (st: ReviewStatus) => {
    const map: Record<ReviewStatus, { bg: string; text: string; icon: any }> = {
      PENDING: { bg: 'bg-amber-50 text-amber-800 border-amber-200', text: 'Pending', icon: Clock },
      IN_REVIEW: { bg: 'bg-blue-50 text-blue-800 border-blue-200', text: 'In Review', icon: Filter },
      RESOLVED: { bg: 'bg-emerald-50 text-emerald-800 border-emerald-200', text: 'Resolved', icon: CheckCircle2 },
      ESCALATED: { bg: 'bg-rose-50 text-rose-800 border-rose-200', text: 'Escalated', icon: AlertTriangle },
      CANCELLED: { bg: 'bg-slate-50 text-slate-600 border-slate-200', text: 'Cancelled', icon: XCircle },
    };
    const c = map[st] || map.PENDING;
    const Icon = c.icon;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${c.bg}`}>
        <Icon className="w-3 h-3 mr-1" /> {c.text}
      </span>
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20 md:pb-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-3 text-civic-teal">
            <ShieldAlert className="w-8 h-8 shrink-0 text-amber-600" />
            <div>
              <h2 className="text-2xl font-bold text-civic-navy">Senior Review Queue & Disagreement Audit</h2>
              <p className="text-sm text-slate-500">
                Persistent PostgreSQL disagreement records. Original human and system grades remain strictly immutable.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowLogModal(true)}
            className="inline-flex items-center px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs rounded-xl shadow-sm transition-colors self-start sm:self-auto"
          >
            <PlusCircle className="w-4 h-4 mr-1.5" /> Flag New Disagreement
          </button>
        </div>

        {/* Stats Pill Bar */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <span className="text-xs text-slate-500 font-medium block">Total Reviews</span>
              <span className="text-xl font-bold text-civic-navy">{stats.total_reviews}</span>
            </div>
            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-center">
              <span className="text-xs text-amber-700 font-medium block">Pending</span>
              <span className="text-xl font-bold text-amber-900">{stats.pending_count}</span>
            </div>
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-center">
              <span className="text-xs text-emerald-700 font-medium block">Resolved</span>
              <span className="text-xl font-bold text-emerald-900">{stats.resolved_count}</span>
            </div>
            <div className="p-3 bg-rose-50 rounded-xl border border-rose-200 text-center">
              <span className="text-xs text-rose-700 font-medium block">Escalated</span>
              <span className="text-xl font-bold text-rose-900">{stats.escalated_count}</span>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex border-b border-slate-200 space-x-1 pt-2">
          {['ALL', 'PENDING', 'IN_REVIEW', 'RESOLVED', 'ESCALATED'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3.5 py-2 text-xs font-bold transition-colors border-b-2 -mb-px ${
                activeTab === tab 
                  ? 'border-civic-teal text-civic-navy' 
                  : 'border-transparent text-slate-400 hover:text-slate-700'
              }`}
            >
              {tab.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Review Cards List */}
      <div className="space-y-3">
        {reviews.length === 0 ? (
          <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
            <h4 className="text-base font-bold text-civic-navy">Review Queue Clear</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No disagreement reviews found in '{activeTab}' status. Human and system predictions are currently aligned.
            </p>
          </div>
        ) : (
          reviews.map((rev) => (
            <div 
              key={rev.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 hover:border-slate-300 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-slate-400">ID: {rev.id.slice(0, 8)}...</span>
                  {statusBadge(rev.status)}
                </div>
                <span className="text-xs text-slate-400">
                  {new Date(rev.created_at).toLocaleDateString()} {new Date(rev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Immutable Comparison Row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-500 font-semibold block flex items-center">
                    <Lock className="w-3 h-3 mr-1 text-slate-400" /> Human Grade
                  </span>
                  <span className="text-lg font-extrabold text-civic-navy">Grade {rev.original_human_grade}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold block flex items-center">
                    <Lock className="w-3 h-3 mr-1 text-slate-400" /> System Grade
                  </span>
                  <span className="text-lg font-extrabold text-amber-700">Grade {rev.original_system_grade}</span>
                </div>
                {rev.expert_grade && (
                  <div>
                    <span className="text-slate-500 font-semibold block">Expert Grade</span>
                    <span className="text-lg font-extrabold text-teal-800">Grade {rev.expert_grade}</span>
                  </div>
                )}
                {rev.reviewer_final_decision && (
                  <div>
                    <span className="text-emerald-700 font-semibold block flex items-center">
                      <FileCheck className="w-3 h-3 mr-1" /> Final Decision
                    </span>
                    <span className="text-lg font-extrabold text-emerald-800">Grade {rev.reviewer_final_decision}</span>
                  </div>
                )}
              </div>

              {/* Rationale & Resolution Notes */}
              <div className="space-y-1.5 text-xs text-slate-600">
                {rev.reviewer_rationale && (
                  <p>
                    <strong className="text-slate-800">Initial Rationale:</strong> {rev.reviewer_rationale}
                  </p>
                )}
                {rev.reviewer_id && (
                  <div className="p-2.5 bg-emerald-50/70 border border-emerald-200 rounded-lg text-emerald-950 font-medium">
                    Resolved by <strong>{rev.reviewer_id}</strong> ({rev.reviewer_action}): Final Authoritative Grade {rev.reviewer_final_decision}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              {rev.status !== 'RESOLVED' && rev.status !== 'CANCELLED' && (
                <div className="flex justify-end pt-1">
                  <button
                    onClick={() => {
                      setSelectedReviewForResolve(rev);
                      setFinalDecision(rev.original_human_grade);
                    }}
                    className="inline-flex items-center px-4 py-2 bg-civic-teal hover:bg-civic-lightTeal text-white font-bold text-xs rounded-xl shadow-sm transition-colors"
                  >
                    <UserCheck className="w-3.5 h-3.5 mr-1.5" /> Adjudicate & Resolve
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Resolution Modal */}
      {selectedReviewForResolve && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2 text-civic-navy font-bold text-base">
                <UserCheck className="w-5 h-5 text-civic-teal" />
                <h3>Senior Review Adjudication</h3>
              </div>
              <button
                onClick={() => setSelectedReviewForResolve(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 space-y-1">
              <div className="font-bold flex items-center">
                <Lock className="w-3.5 h-3.5 mr-1" /> Immutability Guarantee:
              </div>
              <div>Original Human Grade: <strong>Grade {selectedReviewForResolve.original_human_grade}</strong></div>
              <div>Original System Grade: <strong>Grade {selectedReviewForResolve.original_system_grade}</strong></div>
              <div className="text-[11px] text-amber-800 italic mt-1">Original grades are permanently locked in PostgreSQL audit logs.</div>
            </div>

            <form onSubmit={handleResolveSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-civic-navy">Reviewer Identifier</label>
                <input
                  type="text"
                  value={reviewerId}
                  onChange={(e) => setReviewerId(e.target.value)}
                  className="w-full h-11 px-3 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-civic-teal"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-civic-navy">Reviewer Action</label>
                  <select
                    value={reviewerAction}
                    onChange={(e: any) => setReviewerAction(e.target.value)}
                    className="w-full h-11 px-3 rounded-xl border border-slate-300 text-sm font-semibold bg-white"
                  >
                    <option value="UPHELD_HUMAN">Upheld Human Grade</option>
                    <option value="ACCEPTED_SYSTEM">Accepted System Grade</option>
                    <option value="EXPERT_OVERRIDE">Expert Override</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-civic-navy">Authoritative Final Grade</label>
                  <select
                    value={finalDecision}
                    onChange={(e: any) => setFinalDecision(e.target.value)}
                    className="w-full h-11 px-3 rounded-xl border border-slate-300 text-sm font-bold bg-white"
                  >
                    <option value="A">Grade A</option>
                    <option value="B">Grade B</option>
                    <option value="C">Grade C</option>
                    <option value="D">Grade D</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-civic-navy">Clinical Adjudication Rationale</label>
                <textarea
                  rows={3}
                  value={resolutionRationale}
                  onChange={(e) => setResolutionRationale(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-civic-teal"
                  placeholder="State the clinical, physical, or contextual rationale for this final grade determination..."
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedReviewForResolve(null)}
                  className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-bold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resolveMutation.isPending}
                  className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm"
                >
                  Confirm & Resolve Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Disagreement Submission Modal */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2 text-civic-navy font-bold text-base">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                <h3>Flag New Disagreement for Senior Review</h3>
              </div>
              <button
                onClick={() => setShowLogModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-civic-navy">Human Manual Grade</label>
                  <select
                    value={humanGrade}
                    onChange={(e: any) => setHumanGrade(e.target.value)}
                    className="w-full h-11 px-3 rounded-xl border border-slate-300 font-bold bg-white text-sm"
                  >
                    <option value="A">Grade A</option>
                    <option value="B">Grade B</option>
                    <option value="C">Grade C</option>
                    <option value="D">Grade D</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-civic-navy">Rule Engine Grade</label>
                  <select
                    value={systemGrade}
                    onChange={(e: any) => setSystemGrade(e.target.value)}
                    className="w-full h-11 px-3 rounded-xl border border-slate-300 font-bold bg-white text-sm"
                  >
                    <option value="A">Grade A</option>
                    <option value="B">Grade B</option>
                    <option value="C">Grade C</option>
                    <option value="D">Grade D</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-civic-navy">Disagreement Rationale</label>
                <textarea
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-300 text-xs font-medium focus:ring-2 focus:ring-civic-teal"
                  placeholder="Detail why human assessment diverges from automated decision factors..."
                  required
                />
              </div>

              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800 font-medium">
                System Policy: The AI system NEVER overrides human authority. Creating a review logs the event in PostgreSQL for Senior Reviewer adjudication.
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-bold hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-sm"
                >
                  Submit Disagreement Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
