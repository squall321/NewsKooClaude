/**
 * 개선된 로딩 인디케이터
 * 다양한 로딩 상태를 위한 애니메이션
 */

import type { FC } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots' | 'pulse' | 'bar';
  text?: string;
  fullScreen?: boolean;
}

const LoadingIndicator: FC<LoadingIndicatorProps> = ({
  size = 'md',
  variant = 'spinner',
  text,
  fullScreen = false,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const containerClass = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50'
    : 'flex items-center justify-center';

  return (
    <div className={containerClass}>
      <div className="flex flex-col items-center gap-3">
        {variant === 'spinner' && (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Loader2 className={`${sizeClasses[size]} text-primary-600`} />
          </motion.div>
        )}

        {variant === 'dots' && (
          <div className="flex gap-2">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className={`bg-primary-600 rounded-full ${
                  size === 'sm' ? 'w-2 h-2' : size === 'md' ? 'w-3 h-3' : 'w-4 h-4'
                }`}
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: index * 0.2,
                }}
              />
            ))}
          </div>
        )}

        {variant === 'pulse' && (
          <motion.div
            className={`${sizeClasses[size]} bg-primary-600 rounded-full`}
            animate={{ scale: [1, 1.05, 1], opacity: [1, 0.8, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}

        {variant === 'bar' && (
          <div className="w-48 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary-600"
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </div>
        )}

        {text && (
          <motion.p
            className="text-sm text-gray-600 dark:text-gray-400"
            animate={{ scale: [1, 1.05, 1], opacity: [1, 0.8, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          >
            {text}
          </motion.p>
        )}
      </div>
    </div>
  );
};

/**
 * 인라인 스피너
 */
export const InlineSpinner: FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={`inline-block ${className}`}
    >
      <Loader2 className="w-4 h-4" />
    </motion.div>
  );
};

/**
 * 버튼 로딩 상태
 */
export const ButtonLoading: FC<{ text?: string }> = ({ text = 'Loading...' }) => {
  return (
    <span className="flex items-center gap-2">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <Loader2 className="w-4 h-4" />
      </motion.div>
      <span>{text}</span>
    </span>
  );
};

export default LoadingIndicator;
