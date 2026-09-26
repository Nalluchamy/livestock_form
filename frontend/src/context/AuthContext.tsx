import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { UserProfile, loginUser, logoutUser, getCurrentUserProfile } from '../services/authService';
import { localDB } from '../utils/localDatabase';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username_or_email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('elhgs_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize and check current user status
  useEffect(() => {
    let mounted = true;
    async function loadUser() {
      const token = localStorage.getItem('elhgs_access_token');
      if (token) {
        try {
          const profile = await getCurrentUserProfile();
          if (mounted) {
            setUser(profile);
            localStorage.setItem('elhgs_user', JSON.stringify(profile));
          }
        } catch (e) {
          if (mounted) {
            setUser(null);
            localStorage.removeItem('elhgs_user');
            localStorage.removeItem('elhgs_access_token');
            localStorage.removeItem('elhgs_refresh_token');
          }
        }
      }
      if (mounted) setIsLoading(false);
    }

    loadUser();

    const handleExpired = () => {
      setUser(null);
    };
    window.addEventListener('elhgs_session_expired', handleExpired);

    return () => {
      mounted = false;
      window.removeEventListener('elhgs_session_expired', handleExpired);
    };
  }, []);

  const login = async (username_or_email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await loginUser(username_or_email, password);
      localStorage.setItem('elhgs_access_token', data.access_token);
      localStorage.setItem('elhgs_refresh_token', data.refresh_token);
      localStorage.setItem('elhgs_user', JSON.stringify(data.user));
      setUser(data.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('elhgs_refresh_token');
    try {
      if (refreshToken) {
        await logoutUser(refreshToken);
      }
    } catch (e) {
      // Best-effort logout
    } finally {
      // Clear all local session tokens
      localStorage.removeItem('elhgs_access_token');
      localStorage.removeItem('elhgs_refresh_token');
      localStorage.removeItem('elhgs_user');

      // Purge local IndexedDB offline storage for security on logout
      try {
        await localDB.clearAll();
      } catch (dbErr) {
        console.warn('Could not clear local offline DB on logout', dbErr);
      }

      setUser(null);
    }
  };

  const hasRole = useCallback((...roles: string[]): boolean => {
    if (!user) return false;
    if (user.role === 'ADMIN') return true;
    return roles.map((r) => r.toUpperCase()).includes(user.role.toUpperCase());
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
