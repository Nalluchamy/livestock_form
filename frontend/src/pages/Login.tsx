import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, User, AlertCircle, CheckCircle2 } from 'lucide-react';

export const Login: React.FC = () => {
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isDev = import.meta.env.DEV;
  const [username, setUsername] = useState<string>(isDev ? 'admin' : '');
  const [password, setPassword] = useState<string>(isDev ? 'AdminSecurePass2026!' : '');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Login failed. Please verify credentials.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (uname: string, pass: string) => {
    setUsername(uname);
    setPassword(pass);
    setErrorMsg(null);
  };

  if (isAuthenticated && user) {
    return (
      <div className="max-w-md mx-auto mt-12 bg-white rounded-xl shadow-md p-6 text-center border border-slate-200">
        <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-800">Already Authenticated</h2>
        <p className="text-slate-600 mt-2">
          Logged in as <strong className="text-civic-navy">{user.username}</strong> ({user.role})
        </p>
        <button
          onClick={() => navigate('/')}
          className="mt-6 px-4 py-2 bg-civic-teal text-white rounded-lg hover:bg-civic-navy transition-colors font-medium text-sm"
        >
          Go to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto my-8 bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
      <div className="bg-civic-navy text-white px-6 py-5 flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-civic-teal/20 border border-civic-teal/30">
          <Shield className="w-6 h-6 text-civic-teal" />
        </div>
        <div>
          <h2 className="text-lg font-bold">ELHGS Authentication</h2>
          <p className="text-xs text-slate-300">Secure Veterinary Assessment Access</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {errorMsg && (
          <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Username or Email
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-civic-teal focus:border-civic-teal outline-none"
              placeholder="Username or email"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-civic-teal focus:border-civic-teal outline-none"
              placeholder="Enter password"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-civic-teal text-white rounded-lg hover:bg-civic-navy font-semibold text-sm transition-colors shadow-sm disabled:opacity-50"
        >
          {loading ? 'Authenticating...' : 'Sign In'}
        </button>

        {isDev && (
          <div className="pt-4 border-t border-slate-200">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Supervised Pilot Role Presets (Development Only):
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleSelectPreset('admin', 'AdminSecurePass2026!')}
                className="px-2.5 py-1.5 text-left rounded border border-slate-200 hover:bg-slate-50 text-slate-700 transition"
              >
                <div className="font-bold text-civic-navy">Administrator</div>
                <div className="text-[10px] text-slate-500">Superuser Access</div>
              </button>
              <button
                type="button"
                onClick={() => handleSelectPreset('senior_vet', 'SeniorPass2026!')}
                className="px-2.5 py-1.5 text-left rounded border border-slate-200 hover:bg-slate-50 text-slate-700 transition"
              >
                <div className="font-bold text-civic-navy">Senior Reviewer</div>
                <div className="text-[10px] text-slate-500">Adjudicate Consensus</div>
              </button>
              <button
                type="button"
                onClick={() => handleSelectPreset('grader1', 'GraderPass2026!')}
                className="px-2.5 py-1.5 text-left rounded border border-slate-200 hover:bg-slate-50 text-slate-700 transition"
              >
                <div className="font-bold text-civic-navy">Expert Grader 1</div>
                <div className="text-[10px] text-slate-500">Double-Blind Grader</div>
              </button>
              <button
                type="button"
                onClick={() => handleSelectPreset('farmer_dan', 'FarmerPass2026!')}
                className="px-2.5 py-1.5 text-left rounded border border-slate-200 hover:bg-slate-50 text-slate-700 transition"
              >
                <div className="font-bold text-civic-navy">Farmer</div>
                <div className="text-[10px] text-slate-500">Capture & History</div>
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};
