/**
 * 검색 필터 컴포넌트
 * 카테고리, 태그, 날짜 범위, 정렬 옵션
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, X, ChevronDown } from 'lucide-react';
import axiosInstance from '../../lib/axios';

interface Category {
  id: number;
  name: string;
  slug: string;
}

interface Tag {
  id: number;
  name: string;
}

interface DateRange {
  label: string;
  value: string;
  date_from: string;
  date_to: string;
}

interface SearchFiltersProps {
  onFiltersChange: (filters: {
    category?: number;
    tags?: string[];
    dateFrom?: string;
    dateTo?: string;
    sort?: string;
    order?: string;
  }) => void;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ onFiltersChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [dateRanges, setDateRanges] = useState<DateRange[]>([]);

  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedDateRange, setSelectedDateRange] = useState<string>('');
  const [sortBy, setSortBy] = useState('relevance');
  const [sortOrder, setSortOrder] = useState('desc');

  // 필터 옵션 불러오기
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const response = await axiosInstance.get('/api/search/filters');
        const data = response.data.data;

        setCategories(data.categories);
        setTags(data.tags);
        setDateRanges(data.date_ranges);
      } catch (error) {
        console.error('Failed to fetch filters:', error);
      }
    };

    fetchFilters();
  }, []);

  // 필터 변경 시 부모에 전달
  useEffect(() => {
    const selectedRange = dateRanges.find((r) => r.value === selectedDateRange);

    onFiltersChange({
      category: selectedCategory,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      dateFrom: selectedRange?.date_from,
      dateTo: selectedRange?.date_to,
      sort: sortBy,
      order: sortOrder,
    });
  }, [selectedCategory, selectedTags, selectedDateRange, sortBy, sortOrder]);

  const handleCategoryChange = (categoryId: number) => {
    setSelectedCategory(categoryId === selectedCategory ? undefined : categoryId);
  };

  const handleTagToggle = (tagName: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagName) ? prev.filter((t) => t !== tagName) : [...prev, tagName]
    );
  };

  const handleClearFilters = () => {
    setSelectedCategory(undefined);
    setSelectedTags([]);
    setSelectedDateRange('');
    setSortBy('relevance');
    setSortOrder('desc');
  };

  const hasActiveFilters =
    selectedCategory !== undefined ||
    selectedTags.length > 0 ||
    selectedDateRange !== '';

  return (
    <div className="relative">
      {/* 필터 버튼 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <Filter className="w-4 h-4" />
        <span>필터</span>
        {hasActiveFilters && (
          <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
        )}
        <ChevronDown
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* 필터 패널 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700"
          >
            <div className="p-4 space-y-4">
              {/* 헤더 */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  검색 필터
                </h3>
                {hasActiveFilters && (
                  <button
                    onClick={handleClearFilters}
                    className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
                  >
                    초기화
                  </button>
                )}
              </div>

              {/* 카테고리 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  카테고리
                </label>
                <div className="space-y-1">
                  {categories.map((category) => (
                    <label
                      key={category.id}
                      className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    >
                      <input
                        type="radio"
                        name="category"
                        checked={selectedCategory === category.id}
                        onChange={() => handleCategoryChange(category.id)}
                        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-900 dark:text-white">
                        {category.name}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* 태그 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  태그
                </label>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <button
                      key={tag.id}
                      onClick={() => handleTagToggle(tag.name)}
                      className={`px-3 py-1 text-sm rounded-full transition-colors ${
                        selectedTags.includes(tag.name)
                          ? 'bg-primary-500 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {tag.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* 날짜 범위 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  날짜 범위
                </label>
                <select
                  value={selectedDateRange}
                  onChange={(e) => setSelectedDateRange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">전체 기간</option>
                  {dateRanges.map((range) => (
                    <option key={range.value} value={range.value}>
                      {range.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* 정렬 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  정렬
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="relevance">관련도</option>
                    <option value="date">날짜</option>
                    <option value="views">조회수</option>
                    <option value="likes">좋아요</option>
                  </select>

                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="desc">내림차순</option>
                    <option value="asc">오름차순</option>
                  </select>
                </div>
              </div>

              {/* 적용 버튼 */}
              <button
                onClick={() => setIsOpen(false)}
                className="w-full py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                필터 적용
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchFilters;
