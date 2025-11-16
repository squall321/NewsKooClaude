import axiosInstance from '../lib/axios';
import type { WritingStyle } from '../types';

export const writingStylesApi = {
  // Get all writing styles for current user
  getStyles: async (): Promise<WritingStyle[]> => {
    const response = await axiosInstance.get('/api/writing-styles');
    return response.data;
  },

  // Get single style
  getStyle: async (id: number): Promise<WritingStyle> => {
    const response = await axiosInstance.get(`/api/writing-styles/${id}`);
    return response.data;
  },

  // Create new style
  createStyle: async (data: Partial<WritingStyle>): Promise<WritingStyle> => {
    const response = await axiosInstance.post('/api/writing-styles', data);
    return response.data;
  },

  // Update style
  updateStyle: async (id: number, data: Partial<WritingStyle>): Promise<WritingStyle> => {
    const response = await axiosInstance.put(`/api/writing-styles/${id}`, data);
    return response.data;
  },

  // Delete style
  deleteStyle: async (id: number): Promise<void> => {
    await axiosInstance.delete(`/api/writing-styles/${id}`);
  },
};
