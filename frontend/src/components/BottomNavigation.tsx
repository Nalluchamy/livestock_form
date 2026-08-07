import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Camera, History, BarChart3 } from 'lucide-react';

const mobileNavItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/capture', label: 'Grade', icon: Camera },
  { to: '/history', label: 'History', icon: History },
  { to: '/metrics', label: 'Metrics', icon: BarChart3 },
];

export const BottomNavigation: React.FC = () => {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-slate-200 px-2 py-1 shadow-lg">
      <div className="flex justify-around items-center h-14">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center w-full h-full text-xs font-medium transition-colors ${
                  isActive ? 'text-civic-teal font-semibold' : 'text-slate-500 hover:text-slate-800'
                }`
              }
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
