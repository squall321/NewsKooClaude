import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import axiosInstance from '../../lib/axios';
import { Post } from '../../types';
import Card from '../common/Card';
import Skeleton from '../common/Skeleton';

interface PopularPostsProps {
  limit?: number;
  title?: string;
}

const PopularPosts: React.FC<PopularPostsProps> = ({
  limit = 5,
  title = 'Popular Posts',
}) => {
  const { data: posts, isLoading } = useQuery({
    queryKey: ['popular-posts', limit],
    queryFn: async () => {
      const response = await axiosInstance.get<{ data: Post[] }>('/api/posts', {
        params: {
          status: 'published',
          sort: 'views',
          order: 'desc',
          per_page: limit,
        },
      });
      return response.data.data;
    },
  });

  return (
    <Card>
      <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: limit }).map((_, i) => (
            <Skeleton key={i} variant="text" />
          ))}
        </div>
      )}

      {posts && (
        <ul className="space-y-3">
          {posts.map((post, index) => (
            <li key={post.id} className="group">
              <Link
                to={`/post/${post.slug}`}
                className="flex items-start gap-3 hover:bg-gray-50 -mx-2 px-2 py-2 rounded-lg transition-colors"
              >
                <span className="text-2xl font-bold text-gray-300 group-hover:text-primary-600 transition-colors flex-shrink-0">
                  {index + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 group-hover:text-primary-600 line-clamp-2 transition-colors">
                    {post.title}
                  </h4>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <span>{post.views} views</span>
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
};

export default PopularPosts;
