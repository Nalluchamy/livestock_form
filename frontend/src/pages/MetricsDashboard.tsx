import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMetrics, getAgreementMetrics } from '../services/metricsService';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { BarChart3, CheckCircle2, AlertTriangle, Shield, Clock, Search, TrendingUp, Cpu, PieChart } from 'lucide-react';

export const MetricsDashboard: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['metrics'],
    queryFn: getMetrics,
  });

  const { data: agreementData } = useQuery({
    queryKey: ['agreementMetrics'],
    queryFn: getAgreementMetrics,
  });


  if (isLoading) return <LoadingSpinner message="Calculating real-time API metrics..." />;
  if (isError) return <ErrorState message={error instanceof Error ? error.message : 'Failed to fetch metrics'} onRetry={refetch} />;

  return (
    <div className="space-y-6 pb-20 md:pb-6">
      {/* Title Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div>
          <h2 className="text-2xl font-bold text-civic-navy flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-civic-teal" /> Explainability & Performance Dashboard
          </h2>
          <p className="text-sm text-slate-500">
            Empirical evaluation monitoring agreement rates, 3-way model comparison, and error taxonomy breakdown.
          </p>
        </div>

        {data && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            <KpiCard
              title="Total Gradings"
              value={data.total_gradings}
              suggestion="Cumulative total of health evaluations processed."
              icon={BarChart3}
              statusColor="green"
            />
            <KpiCard
              title="Agreement Rate"
              value={`${data.agreement_rate}%`}
              suggestion="High agreement indicates alignment between human graders and Rule Engine."
              icon={CheckCircle2}
              statusColor={data.agreement_rate >= 80 ? 'green' : 'amber'}
            />
            <KpiCard
              title="Disagreement Rate"
              value={`${data.disagreement_rate}%`}
              suggestion="Disagreements trigger Senior Review without overriding humans."
              icon={AlertTriangle}
              statusColor={data.disagreement_rate <= 15 ? 'green' : 'red'}
            />
            <KpiCard
              title="Average Confidence"
              value={`${data.average_confidence}%`}
              suggestion="Confidence drops when observations are missing or contradictory."
              icon={Shield}
              statusColor={data.average_confidence >= 85 ? 'green' : 'amber'}
            />
            <KpiCard
              title="Pending Reviews"
              value={data.pending_reviews}
              suggestion="Evaluations awaiting manual Senior Review verification."
              icon={Clock}
              statusColor={data.pending_reviews === 0 ? 'green' : 'amber'}
            />
            <KpiCard
              title="Low Confidence Cases"
              value={data.low_confidence_cases}
              suggestion="Events below 50% confidence requiring expert observation."
              icon={Search}
              statusColor={data.low_confidence_cases === 0 ? 'green' : 'red'}
            />
          </div>
        )}
      </div>

      {/* Agreement with Expert Grading (Real Validation Set N=32) */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2 text-civic-navy font-bold text-base">
            <CheckCircle2 className="w-5 h-5 text-civic-teal" />
            <h3>Agreement with Expert Grading</h3>
          </div>
          <span className="text-xs font-mono font-semibold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full border border-slate-200">
            [measured, N=32, real validation set]
          </span>
        </div>

        {agreementData ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <span className="text-xs text-slate-500 font-semibold uppercase block">Human Baseline (Inter-Grader)</span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-xl font-bold text-slate-800">κ = {agreementData.human_baseline.cohen_kappa}</span>
                  <span className="text-xs text-slate-600">({agreementData.human_baseline.exact_match_pct}% Match)</span>
                </div>
                <span className="text-[11px] text-slate-500 mt-1 block">Grader 1 vs Grader 2 blind trial</span>
              </div>

              <div className="p-3 bg-teal-50 border border-teal-200 rounded-xl">
                <span className="text-xs text-teal-800 font-semibold uppercase block">Rule Engine vs Consensus</span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-xl font-bold text-teal-900">κ = {agreementData.rule_engine_vs_consensus.cohen_kappa}</span>
                  <span className="text-xs text-teal-700">({agreementData.rule_engine_vs_consensus.exact_match_pct}% Match)</span>
                </div>
                <span className="text-[11px] text-teal-700 mt-1 block">Deterministic rule hierarchy baseline</span>
              </div>

              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                <span className="text-xs text-emerald-800 font-semibold uppercase block">Decision Tree ML vs Consensus</span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-xl font-bold text-emerald-900">κ = {agreementData.decision_tree_ml_vs_consensus.cohen_kappa}</span>
                  <span className="text-xs text-emerald-700">({agreementData.decision_tree_ml_vs_consensus.exact_match_pct}% Match)</span>
                </div>
                <span className="text-[11px] text-emerald-700 mt-1 block">White-box advisory ML model</span>
              </div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5">
              <div className="font-bold text-civic-navy flex items-center">
                <Shield className="w-4 h-4 mr-1 text-civic-teal inline" />
                Plain-Language Expert Alignment Summary:
              </div>
              <p className="text-slate-700">
                Rule Engine achieves <strong>κ = {agreementData.rule_engine_vs_consensus.cohen_kappa}</strong> ({agreementData.rule_engine_vs_consensus.exact_match_pct}% exact match, {agreementData.rule_engine_vs_consensus.adjacent_match_pct}% adjacent match) against expert consensus. The rule engine agrees with experts about as often as independent experts agree with each other (human baseline κ = {agreementData.human_baseline.cohen_kappa}).
              </p>
              <div className="p-2 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 font-medium text-[11px]">
                💡 <strong>Analytical Finding:</strong> The explainable Rule Engine currently agrees with experts more closely than the ML model (κ = {agreementData.rule_engine_vs_consensus.cohen_kappa} vs κ = {agreementData.decision_tree_ml_vs_consensus.cohen_kappa}) on this validation dataset, supporting the Rule Engine as the primary production default.
              </div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-500 italic">Loading real agreement metrics...</div>
        )}
      </div>

      {/* Controlled Experiment Results Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-2 text-civic-teal font-bold text-base">
              <TrendingUp className="w-5 h-5" />
              <h3>Controlled Experiment Results</h3>
            </div>
            <span className="text-xs font-mono font-semibold bg-amber-50 text-amber-800 px-2 py-0.5 rounded border border-amber-200">
              [simulated, experiment_runner.py]
            </span>
          </div>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm font-semibold">
                <span className="text-slate-600">Control Arm (Unassisted Humans)</span>
                <span className="font-bold text-slate-800">68.0% Agreement</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3">
                <div className="bg-slate-400 h-3 rounded-full" style={{ width: '68%' }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-sm font-semibold">
                <span className="text-civic-navy font-bold">ELHGS Arm (AI-Assisted)</span>
                <span className="font-bold text-emerald-600">91.0% Agreement</span>
              </div>
              <div className="w-full bg-emerald-100 rounded-full h-3">
                <div className="bg-emerald-500 h-3 rounded-full" style={{ width: '91%' }} />
              </div>
            </div>

            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-900 space-y-1">
              <div>🎉 71.8% Reduction in Inter-Grader Disputes | 67.3% Time Saved per Evaluation</div>
              <div className="text-[11px] font-normal text-emerald-800 italic">
                Note: Simulated evaluation trial (N=200 trials). Distinguish from measured validation metrics above.
              </div>
            </div>
          </div>
        </div>

        {/* 3-Way Model Benchmarks Section */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-civic-navy font-bold text-base border-b border-slate-100 pb-3">
            <Cpu className="w-5 h-5 text-civic-teal" />
            <h3>3-Way Model Benchmarks</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs">
              <span className="font-bold text-slate-700">Rule Engine (Baseline)</span>
              <span className="font-extrabold text-civic-navy">64.67% Acc | 0.045ms</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs">
              <span className="font-bold text-emerald-900">Decision Tree (Advisory)</span>
              <span className="font-extrabold text-emerald-700">88.17% Acc* | 0.004ms</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-teal-50 border border-teal-200 text-xs">
              <span className="font-bold text-teal-900">Logistic Regression</span>
              <span className="font-extrabold text-teal-700">67.83% Acc | 0.008ms</span>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-1 italic">*Measured on 600 synthetic samples. On N=32 real validation, Rule Engine (κ=0.63) outperforms ML (κ=0.30).</p>
        </div>
      </div>

      {/* Error Taxonomy Section */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-civic-navy font-bold text-base border-b border-slate-100 pb-3">
          <PieChart className="w-5 h-5 text-civic-teal" />
          <h3>Error Taxonomy & Root Cause Analysis</h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
            <span className="text-xs text-slate-500 font-medium block">Borderline BCS</span>
            <span className="text-xl font-bold text-civic-navy">45%</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
            <span className="text-xs text-slate-500 font-medium block">Expert Disagreement</span>
            <span className="text-xl font-bold text-civic-navy">30%</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
            <span className="text-xs text-slate-500 font-medium block">Missing Attributes</span>
            <span className="text-xl font-bold text-civic-navy">15%</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
            <span className="text-xs text-slate-500 font-medium block">Rule Conflict</span>
            <span className="text-xl font-bold text-civic-navy">10%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
