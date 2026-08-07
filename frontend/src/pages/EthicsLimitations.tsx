import React from 'react';
import { ShieldCheck, Lock, UserCheck, AlertOctagon } from 'lucide-react';

export const EthicsLimitations: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-20 md:pb-6">
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center space-x-3 text-civic-teal border-b border-slate-100 pb-4">
          <ShieldCheck className="w-8 h-8" />
          <div>
            <h2 className="text-2xl font-bold text-civic-navy">Ethics & Responsible AI Guardrails</h2>
            <p className="text-sm text-slate-500">
              Ethical principles governing the Explainable Livestock Health Grading System.
            </p>
          </div>
        </div>

        {/* Core Principles */}
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start space-x-3">
            <UserCheck className="w-6 h-6 text-emerald-600 shrink-0 mt-1" />
            <div className="space-y-1">
              <h4 className="font-bold text-emerald-950 text-base">1. Human-in-the-Loop Supremacy</h4>
              <p className="text-sm text-emerald-800 leading-relaxed">
                The AI system exists solely to assist decision-making. The system <strong>MUST NEVER</strong> replace human expert reviewers. Human graders retain absolute final decision authority.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 flex items-start space-x-3">
            <Lock className="w-6 h-6 text-teal-600 shrink-0 mt-1" />
            <div className="space-y-1">
              <h4 className="font-bold text-teal-950 text-base">2. Privacy & Data Ethics</h4>
              <p className="text-sm text-teal-800 leading-relaxed">
                All metadata (EXIF geotags, camera serial numbers, and timestamps) is automatically stripped from livestock images prior to ingestion to prevent unauthorized worker surveillance.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start space-x-3">
            <AlertOctagon className="w-6 h-6 text-amber-600 shrink-0 mt-1" />
            <div className="space-y-1">
              <h4 className="font-bold text-amber-950 text-base">3. Known System Limitations</h4>
              <p className="text-sm text-amber-800 leading-relaxed">
                As a prototype Rule Engine, explanations are derived deterministically. Extremely rare disease presentations or unseen physical traits must be verified by a licensed veterinarian.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
