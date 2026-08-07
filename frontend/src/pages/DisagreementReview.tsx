import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { submitDisagreement } from '../services/disagreementService';
import { AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import { GradeLevel } from '../types';

export const DisagreementReview: React.FC = () => {
  const [humanGrade, setHumanGrade] = useState<GradeLevel>('B');
  const [systemGrade, setSystemGrade] = useState<GradeLevel>('C');
  const [reason, setReason] = useState('Body condition score is borderline 2.0');
  const [submitted, setSubmitted] = useState(false);

  const mutation = useMutation({
    mutationFn: submitDisagreement,
    onSuccess: () => {
      setSubmitted(true);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ human_grade: humanGrade, system_grade: systemGrade, reason });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-20 md:pb-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center space-x-3 text-amber-600">
          <AlertTriangle className="w-7 h-7 shrink-0" />
          <div>
            <h2 className="text-xl font-bold text-civic-navy">Human Disagreement Review Queue</h2>
            <p className="text-sm text-slate-500">
              Senior Reviewers can flag disagreements without overriding human grader authority.
            </p>
          </div>
        </div>

        {submitted ? (
          <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-2xl text-center space-y-3">
            <CheckCircle className="w-12 h-12 text-emerald-600 mx-auto" />
            <h3 className="text-lg font-bold text-emerald-900">Disagreement Logged Successfully</h3>
            <p className="text-sm text-emerald-700">
              The record has been flagged for Senior Review. Human authority remains intact.
            </p>
            <button
              onClick={() => setSubmitted(false)}
              className="mt-2 px-4 py-2 bg-emerald-600 text-white font-bold text-sm rounded-xl"
            >
              Log Another Disagreement
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-bold text-civic-navy">Human Manual Grade</label>
                <select
                  value={humanGrade}
                  onChange={(e) => setHumanGrade(e.target.value as GradeLevel)}
                  className="w-full h-12 px-3 rounded-xl border border-slate-300 font-bold bg-white"
                >
                  <option value="A">Grade A</option>
                  <option value="B">Grade B</option>
                  <option value="C">Grade C</option>
                  <option value="D">Grade D</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-bold text-civic-navy">Rule Engine Grade</label>
                <select
                  value={systemGrade}
                  onChange={(e) => setSystemGrade(e.target.value as GradeLevel)}
                  className="w-full h-12 px-3 rounded-xl border border-slate-300 font-bold bg-white"
                >
                  <option value="A">Grade A</option>
                  <option value="B">Grade B</option>
                  <option value="C">Grade C</option>
                  <option value="D">Grade D</option>
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-bold text-civic-navy">Reason for Disagreement</label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full p-3 rounded-xl border border-slate-300 text-sm font-medium focus:ring-2 focus:ring-civic-teal focus:outline-none"
                placeholder="Describe why human opinion differs from system calculation..."
              />
            </div>

            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 flex items-start space-x-2 text-xs text-amber-800 font-medium">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <span>
                System Policy: The AI system NEVER overrides human authority. Logging a disagreement marks the event for auditing only.
              </span>
            </div>

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full h-12 bg-amber-500 hover:bg-amber-600 text-white font-bold text-sm rounded-xl shadow-sm transition-colors"
            >
              Flag Disagreement for Audit
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
