import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../lib/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      banker: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const data = await authApi.login(email, password);
        localStorage.setItem('bankmind_token', data.access_token);
        set({ token: data.access_token, banker: data.banker, isAuthenticated: true });
        return data;
      },

      logout: () => {
        localStorage.removeItem('bankmind_token');
        set({ token: null, banker: null, isAuthenticated: false });
      },

      hydrate: () => {
        const token = localStorage.getItem('bankmind_token');
        if (token) {
          set({ token, isAuthenticated: true });
        }
      },
    }),
    {
      name: 'bankmind-auth',
      partialize: (state) => ({ banker: state.banker }),
    }
  )
);
