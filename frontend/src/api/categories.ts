import axiosInstance from '../lib/axios';
import type { Category } from '../types';

export const categoriesApi = {
  // Get all categories
  getCategories: async (params?: { page?: number; per_page?: number }): Promise<Category[]> => {
    const response = await axiosInstance.get('/api/categories', { params });
    return response.data;
  },

  // Get single category
  getCategory: async (id: number): Promise<Category> => {
    const response = await axiosInstance.get(`/api/categories/${id}`);
    return response.data;
  },

  // Create category
  createCategory: async (data: Partial<Category>): Promise<Category> => {
    const response = await axiosInstance.post('/api/categories', data);
    return response.data;
  },

  // Update category
  updateCategory: async (id: number, data: Partial<Category>): Promise<Category> => {
    const response = await axiosInstance.put(`/api/categories/${id}`, data);
    return response.data;
  },

  // Delete category
  deleteCategory: async (id: number): Promise<void> => {
    await axiosInstance.delete(`/api/categories/${id}`);
  },
};
