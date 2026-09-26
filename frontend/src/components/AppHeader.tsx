import React from 'react';
import { Activity, ShieldAlert, Cpu, User, LogOut, LogIn } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const AppHeader: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleBadgeColor = (role?: string) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'SENIOR_REVIEWER':
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
      case 'EXPERT_GRADER':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
  };

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
          <span className="hidden lg:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <Cpu className="w-3.5 h-3.5 mr-1" /> AI Assisted
          </span>
          <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            <ShieldAlert className="w-3.5 h-3.5 mr-1" /> Human In The Loop
          </span>

          {/* User Profile Badge & Auth Actions */}
          {isAuthenticated && user ? (
            <div className="flex items-center space-x-2 border-l border-slate-700 pl-3">
              <div className="flex items-center space-x-1.5 bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700 text-xs">
                <User className="w-3.5 h-3.5 text-civic-teal" />
                <span className="font-medium text-slate-200">{user.username}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${getRoleBadgeColor(user.role)}`}>
                  {user.role}
                </span>
              </div>
              <button
                onClick={handleLogout}
                title="Sign Out"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center px-3 py-1.5 rounded-lg bg-civic-teal text-white hover:bg-civic-lightTeal font-semibold text-xs transition shadow-sm"
            >
              <LogIn className="w-3.5 h-3.5 mr-1.5" /> Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
