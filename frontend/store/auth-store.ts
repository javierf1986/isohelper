/**
 * Authentication Store using Zustand
 * Global state management for user authentication
 */

import { create } from 'zustand';
import { authService, User } from '@/lib/auth-service';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (email, password) => {
    const response = await authService.login({ email, password });
    set({ user: response.user, isAuthenticated: true });
  },

  register: async (email, password, fullName) => {
    await authService.register({ email, password, full_name: fullName });
    // After registration, log in automatically
    const response = await authService.login({ email, password });
    set({ user: response.user, isAuthenticated: true });
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: () => {
    const user = authService.getStoredUser();
    const isAuth = authService.isAuthenticated();
    set({ user, isAuthenticated: isAuth, isLoading: false });
  },
}));
