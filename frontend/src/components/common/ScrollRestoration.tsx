import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollRestoration Component
 * Scrolls to top on route change, with smooth behavior
 * Maintains scroll position for back/forward navigation
 */
const ScrollRestoration: React.FC = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    // Scroll to top on route change
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'smooth',
    });
  }, [pathname]);

  return null;
};

export default ScrollRestoration;

/**
 * Hook version for manual control
 */
export const useScrollToTop = () => {
  const scrollToTop = (smooth: boolean = true) => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: smooth ? 'smooth' : 'auto',
    });
  };

  return scrollToTop;
};

/**
 * Save and restore scroll position for specific routes
 */
const scrollPositions = new Map<string, number>();

export const useSaveScrollPosition = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      scrollPositions.set(pathname, window.scrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [pathname]);
};

export const useRestoreScrollPosition = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    const savedPosition = scrollPositions.get(pathname);
    if (savedPosition !== undefined) {
      // Delay to ensure content is rendered
      setTimeout(() => {
        window.scrollTo({
          top: savedPosition,
          left: 0,
          behavior: 'auto',
        });
      }, 0);
    }
  }, [pathname]);
};
