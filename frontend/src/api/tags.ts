import axiosInstance from '../lib/axios';
import { Tag } from '../types';

export const tagsApi = {
  // Get all tags
  getTags: async (params?: { page?: number; per_page?: number }): Promise<Tag[]> => {
    const response = await axiosInstance.get('/api/tags', { params });
    return response.data;
  },

  // Get single tag
  getTag: async (id: number): Promise<Tag> => {
    const response = await axiosInstance.get(`/api/tags/${id}`);
    return response.data;
  },

  // Create tag
  createTag: async (data: Partial<Tag>): Promise<Tag> => {
    const response = await axiosInstance.post('/api/tags', data);
    return response.data;
  },

  // Update tag
  updateTag: async (id: number, data: Partial<Tag>): Promise<Tag> => {
    const response = await axiosInstance.put(`/api/tags/${id}`, data);
    return response.data;
  },

  // Delete tag
  deleteTag: async (id: number): Promise<void> => {
    await axiosInstance.delete(`/api/tags/${id}`);
  },
};
