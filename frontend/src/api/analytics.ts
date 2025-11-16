import axiosInstance from '../lib/axios';
import type { AnalyticsOverview, ContentStats } from '../types';

export const analyticsApi = {
  // Get system overview
  getOverview: async (): Promise<AnalyticsOverview> => {
    const response = await axiosInstance.get('/api/analytics/overview');
    return response.data;
  },

  // Get content stats
  getContentStats: async (params?: { days?: number }): Promise<ContentStats> => {
    const response = await axiosInstance.get('/api/analytics/content-stats', { params });
    return response.data;
  },

  // Get trends
  getTrends: async (params?: { days?: number }): Promise<any> => {
    const response = await axiosInstance.get('/api/analytics/trends', { params });
    return response.data;
  },

  // Get user activity (Admin only)
  getUserActivity: async (): Promise<any> => {
    const response = await axiosInstance.get('/api/analytics/user-activity');
    return response.data;
  },
};
