'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api } from '@/lib/api';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api
        .get<User>('/auth/me')
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      queueMicrotask(() => setIsLoading(false));
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post<{
      id: string;
      name: string;
      email: string;
      role: string;
      email_verified: boolean;
      access_token: string;
      refresh_token: string;
    }>('/auth/login', { email, password });

    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    setUser({
      id: response.id,
      name: response.name,
      email: response.email,
      role: response.role,
      email_verified: response.email_verified,
    });
  };

  const register = async (name: string, email: string, password: string) => {
    const response = await api.post<{
      id: string;
      name: string;
      email: string;
      role: string;
      email_verified: boolean;
      access_token: string;
      refresh_token: string;
    }>('/auth/register', { name, email, password });

    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    setUser({
      id: response.id,
      name: response.name,
      email: response.email,
      role: response.role,
      email_verified: response.email_verified,
    });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
