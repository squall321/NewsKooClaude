/**
 * 댓글 작성 중 표시 컴포넌트
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TypingIndicatorProps {
  typingUsers: string[];
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ typingUsers }) => {
  if (typingUsers.length === 0) {
    return null;
  }

  const displayText = () => {
    if (typingUsers.length === 1) {
      return `${typingUsers[0]}님이 댓글을 작성 중입니다...`;
    } else if (typingUsers.length === 2) {
      return `${typingUsers[0]}님과 ${typingUsers[1]}님이 댓글을 작성 중입니다...`;
    } else {
      return `${typingUsers[0]}님 외 ${typingUsers.length - 1}명이 댓글을 작성 중입니다...`;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-400"
      >
        <div className="flex gap-1">
          <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
            className="w-2 h-2 bg-primary-500 rounded-full"
          />
          <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
            className="w-2 h-2 bg-primary-500 rounded-full"
          />
          <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
            className="w-2 h-2 bg-primary-500 rounded-full"
          />
        </div>
        <span className="italic">{displayText()}</span>
      </motion.div>
    </AnimatePresence>
  );
};

export default TypingIndicator;
