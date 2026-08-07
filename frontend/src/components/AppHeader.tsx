import React from 'react';
import { Activity, ShieldAlert, Cpu } from 'lucide-react';
import { Link } from 'react-router-dom';

export const AppHeader: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 w-full bg-civic-navy text-white shadow-md border-b border-civic-slate">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-lg bg-civic-teal flex items-center justify-center text-white shadow-inner group-hover:bg-civic-lightTeal transition-colors">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-tight">ELHGS</h1>
            <p className="text-xs text-slate-300 font-medium">Explainable Livestock Health</p>
          </div>
        </Link>
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <Cpu className="w-3.5 h-3.5 mr-1" /> AI Assisted
          </span>
          <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            <ShieldAlert className="w-3.5 h-3.5 mr-1" /> Human In The Loop
          </span>
        </div>
      </div>
    </header>
  );
};
