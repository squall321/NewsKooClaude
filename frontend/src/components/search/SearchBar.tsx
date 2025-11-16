/**
 * 고급 검색바 컴포넌트
 * 자동완성, 최근 검색어, 인기 검색어 기능 포함
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Clock, TrendingUp, Loader2 } from 'lucide-react';
import { useDebounce } from '../../hooks/useDebounce';
import axiosInstance from '../../lib/axios';

interface Suggestion {
  text: string;
  type: 'recent' | 'trending' | 'autocomplete';
}

const SearchBar: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [trendingSearches, setTrendingSearches] = useState<string[]>([]);

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const debouncedQuery = useDebounce(query, 300);

  // 최근 검색어 불러오기
  useEffect(() => {
    const recent = localStorage.getItem('recentSearches');
    if (recent) {
      try {
        setRecentSearches(JSON.parse(recent));
      } catch (e) {
        localStorage.removeItem('recentSearches');
      }
    }
  }, []);

  // 인기 검색어 불러오기
  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const response = await axiosInstance.get('/api/search/trending');
        setTrendingSearches(response.data.data.trending.slice(0, 5));
      } catch (error) {
        console.error('Failed to fetch trending searches:', error);
      }
    };

    fetchTrending();
  }, []);

  // 자동완성 검색
  useEffect(() => {
    if (debouncedQuery.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchAutocomplete = async () => {
      setIsLoading(true);
      try {
        const response = await axiosInstance.get('/api/search/autocomplete', {
          params: { q: debouncedQuery, limit: 5 },
        });

        const autocompleteSuggestions: Suggestion[] = response.data.data.suggestions.map(
          (text: string) => ({
            text,
            type: 'autocomplete' as const,
          })
        );

        setSuggestions(autocompleteSuggestions);
      } catch (error) {
        console.error('Autocomplete error:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAutocomplete();
  }, [debouncedQuery]);

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const saveRecentSearch = (searchQuery: string) => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;

    const updated = [trimmed, ...recentSearches.filter((q) => q !== trimmed)].slice(0, 10);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  };

  const handleSearch = (searchQuery: string = query) => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;

    saveRecentSearch(trimmed);
    setIsOpen(false);
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setQuery(suggestion.text);
    handleSearch(suggestion.text);
  };

  const clearRecentSearch = (searchQuery: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = recentSearches.filter((q) => q !== searchQuery);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  };

  const clearAllRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };

  const getDisplaySuggestions = (): Suggestion[] => {
    if (query.trim().length >= 2) {
      return suggestions;
    }

    const displaySuggestions: Suggestion[] = [];

    // 최근 검색어
    if (recentSearches.length > 0) {
      displaySuggestions.push(
        ...recentSearches.slice(0, 5).map((text) => ({
          text,
          type: 'recent' as const,
        }))
      );
    }

    // 인기 검색어
    if (trendingSearches.length > 0 && displaySuggestions.length < 5) {
      displaySuggestions.push(
        ...trendingSearches
          .slice(0, 5 - displaySuggestions.length)
          .map((text) => ({
            text,
            type: 'trending' as const,
          }))
      );
    }

    return displaySuggestions;
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-2xl">
      {/* 검색 입력 */}
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder="검색어를 입력하세요..."
            className="w-full pl-12 pr-12 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />

          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {isLoading && (
            <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
              <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
            </div>
          )}
        </div>
      </form>

      {/* 자동완성/추천 드롭다운 */}
      <AnimatePresence>
        {isOpen && getDisplaySuggestions().length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            {/* 최근 검색어 헤더 */}
            {query.trim().length < 2 && recentSearches.length > 0 && (
              <div className="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  최근 검색어
                </span>
                <button
                  onClick={clearAllRecentSearches}
                  className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  모두 삭제
                </button>
              </div>
            )}

            {/* 추천 목록 */}
            <div className="max-h-96 overflow-y-auto">
              {getDisplaySuggestions().map((suggestion, index) => (
                <motion.div
                  key={`${suggestion.type}-${suggestion.text}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer group"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {suggestion.type === 'recent' && (
                      <Clock className="w-4 h-4 text-gray-400" />
                    )}
                    {suggestion.type === 'trending' && (
                      <TrendingUp className="w-4 h-4 text-primary-500" />
                    )}
                    {suggestion.type === 'autocomplete' && (
                      <Search className="w-4 h-4 text-gray-400" />
                    )}

                    <span className="text-gray-900 dark:text-white">{suggestion.text}</span>
                  </div>

                  {suggestion.type === 'recent' && (
                    <button
                      onClick={(e) => clearRecentSearch(suggestion.text, e)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                    >
                      <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchBar;
