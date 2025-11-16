import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { usePosts } from '../hooks/usePosts';
import PostCard from '../components/post/PostCard';
import { SkeletonPostCard } from '../components/common/Skeleton';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';
import Button from '../components/common/Button';
import SEO from '../components/common/SEO';
import NativeAd from '../components/ads/NativeAd';
import { staggerContainer, fadeInUp } from '../lib/animations';

type SortOption = 'latest' | 'popular' | 'trending';

const Home: React.FC = () => {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortOption>('latest');

  const getSortParams = () => {
    switch (sortBy) {
      case 'popular':
        return { sort: 'views', order: 'desc' };
      case 'trending':
        return { sort: 'created_at', order: 'desc' }; // TODO: implement trending logic
      default:
        return { sort: 'published_at', order: 'desc' };
    }
  };

  const { data, isLoading, error } = usePosts({
    page,
    per_page: 12,
    status: 'published',
    ...getSortParams(),
  });

  const loadMoreRef = useInfiniteScroll({
    onLoadMore: () => {
      if (data?.meta.has_next) {
        setPage((prev) => prev + 1);
      }
    },
    hasMore: data?.meta.has_next || false,
    isLoading,
  });

  if (error) {
    return (
      <div className="container-custom py-12">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Oops! Something went wrong
          </h2>
          <p className="text-gray-600 mb-6">Failed to load posts. Please try again later.</p>
          <Button onClick={() => window.location.reload()}>Reload Page</Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="NewsKoo - 전 세계의 유머, 한국식으로"
        description="Reddit, Twitter의 재미있는 이야기를 AI가 한국 문화에 맞게 재해석합니다. 매일 새로운 유머 콘텐츠를 만나보세요."
        keywords={['유머', '한국어', '재미있는 이야기', 'Reddit 번역', 'AI 번역', '한국 유머', '웃긴 글']}
        url="/"
      />
      <div className="bg-gray-50 min-h-screen">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-16">
        <motion.div
          className="container-custom"
          initial="initial"
          animate="animate"
          variants={fadeInUp}
        >
          <h1 className="text-4xl md:text-5xl font-display font-bold mb-4">
            전 세계의 유머, 한국식으로 😄
          </h1>
          <p className="text-xl text-primary-100 max-w-2xl">
            Reddit, Twitter의 재미있는 이야기를 AI가 한국 문화에 맞게 재해석합니다
          </p>
        </motion.div>
      </section>

      {/* Posts Grid */}
      <section className="container-custom py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Latest Stories</h2>
          <div className="flex gap-2">
            <Button
              variant={sortBy === 'latest' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {
                setSortBy('latest');
                setPage(1);
              }}
            >
              Latest
            </Button>
            <Button
              variant={sortBy === 'popular' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {
                setSortBy('popular');
                setPage(1);
              }}
            >
              Popular
            </Button>
            <Button
              variant={sortBy === 'trending' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => {
                setSortBy('trending');
                setPage(1);
              }}
            >
              Trending
            </Button>
          </div>
        </div>

        {/* Posts Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="initial"
          animate="animate"
          variants={staggerContainer}
        >
          {data?.data.map((post, index) => (
            <React.Fragment key={post.id}>
              <PostCard post={post} />
              {/* Insert ads at position 3 and 7 */}
              {(index === 2 || index === 6) && <NativeAd position={index} />}
            </React.Fragment>
          ))}

          {/* Loading Skeletons */}
          {isLoading &&
            Array.from({ length: 6 }).map((_, index) => (
              <SkeletonPostCard key={`skeleton-${index}`} />
            ))}
        </motion.div>

        {/* No Posts */}
        {!isLoading && data?.data.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No posts yet
            </h3>
            <p className="text-gray-600">
              Check back later for new content!
            </p>
          </div>
        )}

        {/* Infinite Scroll Trigger */}
        <div ref={loadMoreRef} className="h-10" />

        {/* Load More Button (Fallback) */}
        {data?.meta.has_next && !isLoading && (
          <div className="text-center mt-8">
            <Button
              variant="outline"
              onClick={() => setPage((prev) => prev + 1)}
            >
              Load More
            </Button>
          </div>
        )}
      </section>
    </div>
    </>
  );
};

export default Home;
