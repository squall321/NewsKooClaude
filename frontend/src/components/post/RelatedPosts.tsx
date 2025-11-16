import React from 'react';
// import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '../../lib/axios';
import type { Post } from '../../types';
import PostCard from '../post/PostCard';
import { SkeletonPostCard } from '../common/Skeleton';

interface RelatedPostsProps {
  currentPostId: number;
  categoryId?: number;
}

const RelatedPosts: React.FC<RelatedPostsProps> = ({ currentPostId, categoryId }) => {
  const { data: posts, isLoading } = useQuery({
    queryKey: ['related-posts', currentPostId, categoryId],
    queryFn: async () => {
      const params: any = {
        per_page: 3,
        status: 'published',
      };
      if (categoryId) {
        params.category_id = categoryId;
      }
      const response = await axiosInstance.get<{ data: Post[] }>('/api/posts', { params });
      // Filter out current post
      return response.data.data.filter(post => post.id !== currentPostId);
    },
  });

  if (isLoading) {
    return (
      <div>
        <h2 className="text-2xl font-bold mb-6">Related Stories</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonPostCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (!posts || posts.length === 0) {
    return null;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Related Stories</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {posts.slice(0, 3).map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
};

export default RelatedPosts;
