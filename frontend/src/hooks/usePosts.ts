import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { postsApi } from '../api/posts';
import type { Post } from '../types';

export const usePosts = (params?: {
  page?: number;
  per_page?: number;
  status?: 'draft' | 'published' | 'hidden';
  category_id?: number;
  search?: string;
}) => {
  return useQuery({
    queryKey: ['posts', params],
    queryFn: () => postsApi.getPosts(params),
  });
};

export const usePost = (id: number) => {
  return useQuery({
    queryKey: ['post', id],
    queryFn: () => postsApi.getPost(id),
    enabled: !!id,
  });
};

export const useCreatePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Post>) => postsApi.createPost(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};

export const useUpdatePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Post> }) =>
      postsApi.updatePost(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};

export const useDeletePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => postsApi.deletePost(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};

export const usePublishPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => postsApi.publishPost(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};

export const useHidePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => postsApi.hidePost(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
};
