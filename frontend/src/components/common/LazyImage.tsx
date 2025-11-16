import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { imageLoad } from '../../lib/animations-enhanced';

interface LazyImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholderSrc?: string;
  threshold?: number;
  onLoad?: () => void;
  onError?: () => void;
  aspectRatio?: string; // e.g., "16/9", "4/3", "1/1"
}

/**
 * Lazy Loading Image Component
 * - Uses Intersection Observer for efficient lazy loading
 * - Shows placeholder while loading
 * - Smooth fade-in animation when loaded
 * - Handles loading and error states
 */
const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholderSrc,
  threshold = 0.1,
  onLoad,
  onError,
  aspectRatio,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // Create Intersection Observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            // Unobserve after it's in view
            if (observerRef.current && imgRef.current) {
              observerRef.current.unobserve(imgRef.current);
            }
          }
        });
      },
      {
        threshold,
        rootMargin: '50px', // Start loading 50px before entering viewport
      }
    );

    // Start observing
    if (imgRef.current) {
      observerRef.current.observe(imgRef.current);
    }

    // Cleanup
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [threshold]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Default placeholder (blurred gradient)
  const defaultPlaceholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23f0f0f0"/%3E%3Cstop offset="100%25" stop-color="%23e0e0e0"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="400" height="300" fill="url(%23g)"/%3E%3C/svg%3E';

  const containerStyle = aspectRatio
    ? { aspectRatio, position: 'relative' as const }
    : {};

  return (
    <div className={`relative overflow-hidden ${className}`} style={containerStyle}>
      <AnimatePresence mode="wait">
        {!isLoaded && !hasError && (
          <motion.div
            key="placeholder"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-gray-200"
          >
            {/* Placeholder image */}
            <img
              src={placeholderSrc || defaultPlaceholder}
              alt=""
              className="w-full h-full object-cover blur-sm"
              aria-hidden="true"
            />
            {/* Loading animation */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
          </motion.div>
        )}

        {hasError && (
          <motion.div
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 flex items-center justify-center bg-gray-100"
          >
            <div className="text-center text-gray-400">
              <svg
                className="w-12 h-12 mx-auto mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-sm">이미지를 불러올 수 없습니다</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actual image - only load when in view */}
      {isInView && !hasError && (
        <motion.img
          ref={imgRef}
          src={src}
          alt={alt}
          className={`w-full h-full object-cover ${isLoaded ? '' : 'opacity-0'}`}
          onLoad={handleLoad}
          onError={handleError}
          variants={imageLoad}
          initial="initial"
          animate={isLoaded ? "animate" : "initial"}
          loading="lazy"
        />
      )}
    </div>
  );
};

export default LazyImage;

/**
 * Memoized version for performance
 */
export const MemoizedLazyImage = React.memo(LazyImage);
