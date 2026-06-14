import { create } from 'zustand';
import { dashboardApi, customersApi } from '../lib/api';

export const useDashboardStore = create((set, get) => ({
  kpis: null,
  pipeline: null,
  activityFeed: [],
  customers: [],
  loading: false,
  error: null,
  lastUpdated: null,
  demoComplete: false,

  fetchKpis: async () => {
    try {
      const kpis = await dashboardApi.kpis();
      set({ kpis });
    } catch (e) {
      set({ error: e.message });
    }
  },

  fetchPipeline: async () => {
    try {
      const pipeline = await dashboardApi.pipeline();
      set({ pipeline });
    } catch (e) {
      set({ error: e.message });
    }
  },

  fetchActivityFeed: async () => {
    try {
      const feed = await dashboardApi.activityFeed();
      set({ activityFeed: feed });
    } catch (e) {
      set({ error: e.message });
    }
  },

  fetchAll: async () => {
    set({ loading: true });
    await Promise.all([
      get().fetchKpis(),
      get().fetchPipeline(),
      get().fetchActivityFeed(),
    ]);
    set({ loading: false, lastUpdated: new Date() });
  },

  prependFeedEntry: (entry) => {
    set((state) => ({
      activityFeed: [{ ...entry, _new: true }, ...state.activityFeed.slice(0, 49)],
    }));
  },

  setDemoComplete: (val) => set({ demoComplete: val }),

  clearError: () => set({ error: null }),
}));
