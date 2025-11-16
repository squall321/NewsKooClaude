/**
 * 검색 결과 페이지
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search as SearchIcon, Loader2 } from 'lucide-react';
import SearchBar from '../components/search/SearchBar';
import SearchFilters from '../components/search/SearchFilters';
import PostCard from '../components/common/PostCard';
import Pagination from '../components/common/Pagination';
import axiosInstance from '../lib/axios';
import { staggerContainer, staggerItem } from '../lib/animations';

interface Post {
  id: number;
  title: string;
  content: string;
  slug: string;
  image_url?: string;
  category?: {
    id: number;
    name: string;
  };
  tags: { id: number; name: string }[];
  views: number;
  likes_count: number;
  comments_count: number;
  created_at: string;
}

interface SearchResult {
  posts: Post[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const [results, setResults] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<any>({});
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  // 검색 실행
  useEffect(() => {
    if (!query.trim()) {
      setResults(null);
      return;
    }

    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const params: any = {
          q: query,
          page: currentPage,
          per_page: 20,
          ...filters,
        };

        // 태그 배열을 쉼표로 구분된 문자열로 변환
        if (params.tags && Array.isArray(params.tags)) {
          params.tags = params.tags.join(',');
        }

        const response = await axiosInstance.get('/api/search', { params });

        setResults(response.data.data);
      } catch (err: any) {
        console.error('Search error:', err);
        setError(err.response?.data?.error || '검색 중 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [query, currentPage, filters]);

  const handleFiltersChange = (newFilters: any) => {
    setFilters(newFilters);
    // 필터 변경 시 첫 페이지로
    if (currentPage !== 1) {
      searchParams.set('page', '1');
      setSearchParams(searchParams);
    }
  };

  const handlePageChange = (page: number) => {
    searchParams.set('page', page.toString());
    setSearchParams(searchParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 검색바 */}
        <div className="mb-8">
          <SearchBar />
        </div>

        {/* 검색어 표시 및 필터 */}
        {query && (
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                "{query}" 검색 결과
              </h1>
              {results && (
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  총 {results.total.toLocaleString()}개의 결과를 찾았습니다
                </p>
              )}
            </div>

            <SearchFilters onFiltersChange={handleFiltersChange} />
          </div>
        )}

        {/* 로딩 상태 */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
            <p className="text-gray-600 dark:text-gray-400">검색 중...</p>
          </div>
        )}

        {/* 에러 상태 */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* 검색 결과 */}
        {!isLoading && !error && results && (
          <>
            {results.posts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20">
                <SearchIcon className="w-16 h-16 text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  검색 결과가 없습니다
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
                  다른 검색어를 시도하거나 필터를 변경해보세요.
                </p>
              </div>
            ) : (
              <>
                {/* 검색 결과 목록 */}
                <motion.div
                  variants={staggerContainer}
                  initial="initial"
                  animate="animate"
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
                >
                  {results.posts.map((post) => (
                    <motion.div key={post.id} variants={staggerItem}>
                      <PostCard
                        id={post.id}
                        title={post.title}
                        excerpt={post.content}
                        imageUrl={post.image_url}
                        category={post.category?.name}
                        tags={post.tags.map((t) => t.name)}
                        views={post.views}
                        likes={post.likes_count}
                        comments={post.comments_count}
                        publishedAt={post.created_at}
                        slug={post.slug}
                      />
                    </motion.div>
                  ))}
                </motion.div>

                {/* 페이지네이션 */}
                {results.pages > 1 && (
                  <div className="flex justify-center">
                    <Pagination
                      currentPage={currentPage}
                      totalPages={results.pages}
                      onPageChange={handlePageChange}
                    />
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* 검색어 없음 */}
        {!query && (
          <div className="flex flex-col items-center justify-center py-20">
            <SearchIcon className="w-16 h-16 text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              검색어를 입력하세요
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
              원하시는 콘텐츠를 찾기 위해 검색어를 입력해주세요.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;
