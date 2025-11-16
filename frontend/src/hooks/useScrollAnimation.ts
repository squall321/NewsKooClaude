/**
 * 스크롤 애니메이션 Hook
 * Intersection Observer를 활용한 뷰포트 진입 애니메이션
 */

import { useEffect, useRef, useState } from 'react';
import { useInView } from 'framer-motion';

interface UseScrollAnimationOptions {
  threshold?: number;
  triggerOnce?: boolean;
  rootMargin?: string;
}

/**
 * 요소가 뷰포트에 진입했는지 감지
 */
export const useScrollAnimation = (options: UseScrollAnimationOptions = {}) => {
  const { threshold = 0.1, triggerOnce = true, rootMargin = '0px' } = options;
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, {
    once: triggerOnce,
    margin: rootMargin,
    amount: threshold,
  });

  return { ref, isInView };
};

/**
 * 스크롤 방향 감지
 */
export const useScrollDirection = () => {
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down' | null>(null);
  const [prevScrollY, setPrevScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY > prevScrollY && currentScrollY > 50) {
        setScrollDirection('down');
      } else if (currentScrollY < prevScrollY) {
        setScrollDirection('up');
      }

      setPrevScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [prevScrollY]);

  return scrollDirection;
};

/**
 * 스크롤 진행률 추적
 */
export const useScrollProgress = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const calculateProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY;

      const totalScroll = documentHeight - windowHeight;
      const currentProgress = (scrollTop / totalScroll) * 100;

      setProgress(Math.min(Math.max(currentProgress, 0), 100));
    };

    window.addEventListener('scroll', calculateProgress, { passive: true });
    calculateProgress(); // Initial calculation

    return () => window.removeEventListener('scroll', calculateProgress);
  }, []);

  return progress;
};

/**
 * 부드러운 스크롤
 */
export const smoothScrollTo = (
  targetY: number,
  duration: number = 1000,
  easing: (t: number) => number = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
) => {
  const startY = window.scrollY;
  const distance = targetY - startY;
  const startTime = performance.now();

  const scroll = () => {
    const currentTime = performance.now();
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const easedProgress = easing(progress);
    const newY = startY + distance * easedProgress;

    window.scrollTo(0, newY);

    if (progress < 1) {
      requestAnimationFrame(scroll);
    }
  };

  requestAnimationFrame(scroll);
};

/**
 * 요소로 부드럽게 스크롤
 */
export const smoothScrollToElement = (
  element: HTMLElement | null,
  offset: number = 0,
  duration: number = 1000
) => {
  if (!element) return;

  const targetY = element.getBoundingClientRect().top + window.scrollY + offset;
  smoothScrollTo(targetY, duration);
};

/**
 * 무한 스크롤
 */
export const useInfiniteScroll = (
  callback: () => void,
  options: { threshold?: number; rootMargin?: string } = {}
) => {
  const { threshold = 0.1, rootMargin = '200px' } = options;
  const observerRef = useRef<IntersectionObserver | null>(null);
  const targetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!targetRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          callback();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observerRef.current.observe(targetRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [callback, threshold, rootMargin]);

  return targetRef;
};

/**
 * 패럴랙스 스크롤 효과
 */
export const useParallax = (speed: number = 0.5) => {
  const [offsetY, setOffsetY] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!ref.current) return;

      const rect = ref.current.getBoundingClientRect();
      const scrolled = window.scrollY;

      // 요소가 뷰포트에 있을 때만 계산
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        setOffsetY((rect.top - window.innerHeight) * speed);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial calculation

    return () => window.removeEventListener('scroll', handleScroll);
  }, [speed]);

  return { ref, offsetY };
};
