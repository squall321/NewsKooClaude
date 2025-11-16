/**
 * 페이지 전환 애니메이션 래퍼
 * 모든 페이지에 일관된 전환 효과 제공
 */

import type { FC, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { pageTransition } from '../../lib/animations-enhanced';

interface AnimatedPageProps {
  children: ReactNode;
  className?: string;
}

const AnimatedPage: FC<AnimatedPageProps> = ({ children, className = '' }) => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        variants={pageTransition}
        initial="initial"
        animate="animate"
        exit="exit"
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

export default AnimatedPage;
