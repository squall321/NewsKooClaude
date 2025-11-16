import axiosInstance from '../lib/axios';
import { Post, PaginatedResponse } from '../types';

export const postsApi = {
  // Get all posts with pagination and filters
  getPosts: async (params?: {
    page?: number;
    per_page?: number;
    status?: 'draft' | 'published' | 'hidden';
    category_id?: number;
    search?: string;
  }): Promise<PaginatedResponse<Post>> => {
    const response = await axiosInstance.get('/api/posts', { params });
    return response.data;
  },

  // Get single post by ID
  getPost: async (id: number): Promise<Post> => {
    const response = await axiosInstance.get(`/api/posts/${id}`);
    return response.data;
  },

  // Create new post
  createPost: async (data: Partial<Post>): Promise<Post> => {
    const response = await axiosInstance.post('/api/posts', data);
    return response.data;
  },

  // Update post
  updatePost: async (id: number, data: Partial<Post>): Promise<Post> => {
    const response = await axiosInstance.put(`/api/posts/${id}`, data);
    return response.data;
  },

  // Delete post
  deletePost: async (id: number): Promise<void> => {
    await axiosInstance.delete(`/api/posts/${id}`);
  },

  // Publish post
  publishPost: async (id: number): Promise<Post> => {
    const response = await axiosInstance.post(`/api/posts/${id}/publish`);
    return response.data;
  },

  // Hide post
  hidePost: async (id: number): Promise<Post> => {
    const response = await axiosInstance.post(`/api/posts/${id}/hide`);
    return response.data;
  },
};
