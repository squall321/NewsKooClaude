/**
 * 스와이프 제스처 지원 컴포넌트
 * 모바일 UX 향상
 */

import type { FC, ReactNode } from 'react';
import type { PanInfo } from 'framer-motion';
import { motion, useAnimation } from 'framer-motion';

interface SwipeableProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
  className?: string;
}

const Swipeable: FC<SwipeableProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 100,
  className = '',
}) => {
  const controls = useAnimation();

  const handleDragEnd = (_: any, info: PanInfo) => {
    const { offset } = info;

    // 수평 스와이프
    if (Math.abs(offset.x) > Math.abs(offset.y)) {
      if (offset.x > threshold && onSwipeRight) {
        onSwipeRight();
      } else if (offset.x < -threshold && onSwipeLeft) {
        onSwipeLeft();
      }
    }
    // 수직 스와이프
    else {
      if (offset.y > threshold && onSwipeDown) {
        onSwipeDown();
      } else if (offset.y < -threshold && onSwipeUp) {
        onSwipeUp();
      }
    }

    // 원래 위치로 복귀
    controls.start({
      x: 0,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 30,
      },
    });
  };

  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      animate={controls}
      className={className}
      style={{ touchAction: 'pan-y' }} // 수직 스크롤 허용
    >
      {children}
    </motion.div>
  );
};

export default Swipeable;
