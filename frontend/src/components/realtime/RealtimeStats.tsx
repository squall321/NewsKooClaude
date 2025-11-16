/**
 * 실시간 통계 표시 컴포넌트
 * 게시물 조회수, 좋아요 수 실시간 업데이트
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Eye } from 'lucide-react';
import { usePostStats } from '../../hooks/useSocket';

interface RealtimeStatsProps {
  postId: number;
  initialLikes: number;
  initialViews: number;
}

const RealtimeStats: React.FC<RealtimeStatsProps> = ({
  postId,
  initialLikes,
  initialViews,
}) => {
  const [likes, setLikes] = useState(initialLikes);
  const [views, setViews] = useState(initialViews);
  const [likesIncreased, setLikesIncreased] = useState(false);
  const [viewsIncreased, setViewsIncreased] = useState(false);

  usePostStats(
    postId,
    // 좋아요 업데이트 콜백
    (newLikes) => {
      if (newLikes > likes) {
        setLikesIncreased(true);
        setTimeout(() => setLikesIncreased(false), 1000);
      }
      setLikes(newLikes);
    },
    // 조회수 업데이트 콜백
    (newViews) => {
      if (newViews > views) {
        setViewsIncreased(true);
        setTimeout(() => setViewsIncreased(false), 1000);
      }
      setViews(newViews);
    }
  );

  return (
    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
      {/* 좋아요 */}
      <motion.div
        className="flex items-center gap-1"
        animate={likesIncreased ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 0.3 }}
      >
        <Heart
          className={`w-4 h-4 ${likesIncreased ? 'text-red-500' : ''}`}
          fill={likesIncreased ? 'currentColor' : 'none'}
        />
        <AnimatePresence mode="wait">
          <motion.span
            key={likes}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className={likesIncreased ? 'text-red-500 font-semibold' : ''}
          >
            {likes.toLocaleString()}
          </motion.span>
        </AnimatePresence>
      </motion.div>

      {/* 조회수 */}
      <motion.div
        className="flex items-center gap-1"
        animate={viewsIncreased ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 0.3 }}
      >
        <Eye className={`w-4 h-4 ${viewsIncreased ? 'text-blue-500' : ''}`} />
        <AnimatePresence mode="wait">
          <motion.span
            key={views}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className={viewsIncreased ? 'text-blue-500 font-semibold' : ''}
          >
            {views.toLocaleString()}
          </motion.span>
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default RealtimeStats;
