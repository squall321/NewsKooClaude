/**
 * 스크롤 진행률 표시 바
 * 페이지 읽기 진행률 시각화
 */

import React from 'react';
import { motion, useScroll, useSpring } from 'framer-motion';

interface ProgressBarProps {
  position?: 'top' | 'bottom';
  color?: string;
  height?: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  position = 'top',
  color = 'bg-primary-600',
  height = 3,
}) => {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  const positionClass = position === 'top' ? 'top-0' : 'bottom-0';

  return (
    <motion.div
      className={`fixed left-0 right-0 ${positionClass} ${color} origin-left z-50`}
      style={{
        scaleX,
        height: `${height}px`,
      }}
    />
  );
};

export default ProgressBar;
