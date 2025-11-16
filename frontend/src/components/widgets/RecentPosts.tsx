import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import axiosInstance from '../../lib/axios';
import { Post } from '../../types';
import Card from '../common/Card';
import Skeleton from '../common/Skeleton';

interface RecentPostsProps {
  limit?: number;
  title?: string;
}

const RecentPosts: React.FC<RecentPostsProps> = ({
  limit = 5,
  title = 'Recent Posts',
}) => {
  const { data: posts, isLoading } = useQuery({
    queryKey: ['recent-posts', limit],
    queryFn: async () => {
      const response = await axiosInstance.get<{ data: Post[] }>('/api/posts', {
        params: {
          status: 'published',
          sort: 'published_at',
          order: 'desc',
          per_page: limit,
        },
      });
      return response.data.data;
    },
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

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
          {posts.map((post) => (
            <li key={post.id} className="group">
              <Link
                to={`/post/${post.slug}`}
                className="block hover:bg-gray-50 -mx-2 px-2 py-2 rounded-lg transition-colors"
              >
                <h4 className="text-sm font-medium text-gray-900 group-hover:text-primary-600 line-clamp-2 mb-1 transition-colors">
                  {post.title}
                </h4>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{formatDate(post.published_at || post.created_at)}</span>
                  <span>•</span>
                  <span>{post.views} views</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
};

export default RecentPosts;
