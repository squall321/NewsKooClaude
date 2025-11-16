import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '../lib/axios';
import { Post } from '../types';
import PostCard from '../components/post/PostCard';
import { SkeletonPostCard } from '../components/common/Skeleton';
import Input from '../components/common/Input';

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') || '');
  const [debouncedSearch, setDebouncedSearch] = useState(searchTerm);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Update URL when debounced search changes
  useEffect(() => {
    if (debouncedSearch) {
      setSearchParams({ q: debouncedSearch });
    } else {
      setSearchParams({});
    }
  }, [debouncedSearch, setSearchParams]);

  const { data, isLoading } = useQuery({
    queryKey: ['search', debouncedSearch],
    queryFn: async () => {
      if (!debouncedSearch) return { data: [], meta: { total: 0 } };
      const response = await axiosInstance.get('/api/posts', {
        params: {
          search: debouncedSearch,
          status: 'published',
          per_page: 20,
        },
      });
      return response.data;
    },
    enabled: debouncedSearch.length >= 2,
  });

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Search Header */}
      <section className="bg-white border-b border-gray-200 py-8">
        <div className="container-custom">
          <h1 className="text-3xl font-display font-bold mb-6">Search Posts</h1>
          <div className="max-w-2xl">
            <Input
              type="text"
              placeholder="Search for posts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="text-lg"
            />
          </div>
          {debouncedSearch && (
            <div className="mt-4 text-gray-600">
              {isLoading ? (
                'Searching...'
              ) : (
                <>
                  Found {data?.meta.total || 0} result{data?.meta.total !== 1 ? 's' : ''} for "
                  <span className="font-semibold">{debouncedSearch}</span>"
                </>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Search Results */}
      <section className="container-custom py-12">
        {!debouncedSearch && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start searching
            </h3>
            <p className="text-gray-600">
              Enter at least 2 characters to search for posts
            </p>
          </div>
        )}

        {debouncedSearch && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.data.map((post: Post) => (
              <PostCard key={post.id} post={post} />
            ))}

            {/* Loading Skeletons */}
            {isLoading &&
              Array.from({ length: 6 }).map((_, index) => (
                <SkeletonPostCard key={`skeleton-${index}`} />
              ))}
          </div>
        )}

        {/* No Results */}
        {!isLoading && debouncedSearch && data?.data.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">😕</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No results found
            </h3>
            <p className="text-gray-600">
              Try searching with different keywords
            </p>
          </div>
        )}
      </section>
    </div>
  );
};

export default SearchPage;
