import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '../lib/axios';
import { Category, Post } from '../types';
import PostCard from '../components/post/PostCard';
import { SkeletonPostCard } from '../components/common/Skeleton';
import Button from '../components/common/Button';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';

const CategoryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [page, setPage] = useState(1);

  // Get category info
  const { data: category } = useQuery({
    queryKey: ['category', slug],
    queryFn: async () => {
      const response = await axiosInstance.get<Category>(`/api/categories/slug/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });

  // Get posts in this category
  const { data: postsData, isLoading } = useQuery({
    queryKey: ['category-posts', category?.id, page],
    queryFn: async () => {
      const response = await axiosInstance.get('/api/posts', {
        params: {
          category_id: category?.id,
          status: 'published',
          page,
          per_page: 12,
        },
      });
      return response.data;
    },
    enabled: !!category?.id,
  });

  const loadMoreRef = useInfiniteScroll({
    onLoadMore: () => {
      if (postsData?.meta.has_next) {
        setPage((prev) => prev + 1);
      }
    },
    hasMore: postsData?.meta.has_next || false,
    isLoading,
  });

  if (!category) {
    return (
      <div className="container-custom py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Category not found</h2>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Category Header */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-12">
        <div className="container-custom">
          <h1 className="text-4xl font-display font-bold mb-4">{category.name}</h1>
          {category.description && (
            <p className="text-xl text-primary-100 max-w-2xl">{category.description}</p>
          )}
          <div className="mt-4 text-primary-100">
            {postsData?.meta.total || 0} posts
          </div>
        </div>
      </section>

      {/* Posts Grid */}
      <section className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {postsData?.data.map((post: Post) => (
            <PostCard key={post.id} post={post} />
          ))}

          {/* Loading Skeletons */}
          {isLoading &&
            Array.from({ length: 6 }).map((_, index) => (
              <SkeletonPostCard key={`skeleton-${index}`} />
            ))}
        </div>

        {/* No Posts */}
        {!isLoading && postsData?.data.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No posts in this category yet
            </h3>
            <p className="text-gray-600">Check back later for new content!</p>
          </div>
        )}

        {/* Infinite Scroll Trigger */}
        <div ref={loadMoreRef} className="h-10" />

        {/* Load More Button (Fallback) */}
        {postsData?.meta.has_next && !isLoading && (
          <div className="text-center mt-8">
            <Button variant="outline" onClick={() => setPage((prev) => prev + 1)}>
              Load More
            </Button>
          </div>
        )}
      </section>
    </div>
  );
};

export default CategoryPage;
