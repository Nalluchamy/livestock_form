import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Camera, History, BarChart3, ShieldCheck, AlertTriangle } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/capture', label: 'Capture Grade', icon: Camera },
  { to: '/history', label: 'Grading History', icon: History },
  { to: '/disagreements', label: 'Disagreements', icon: AlertTriangle },
  { to: '/metrics', label: 'Metrics', icon: BarChart3 },
  { to: '/ethics', label: 'Ethics & Guardrails', icon: ShieldCheck },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-16 bg-white border-r border-slate-200 p-4 space-y-1">
      <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
        Navigation
      </div>
      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-colors ${
                isActive
                  ? 'bg-civic-teal text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </aside>
  );
};
