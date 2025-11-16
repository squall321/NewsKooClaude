import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

interface PerformanceMetrics {
  fcp?: number; // First Contentful Paint
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
  ttfb?: number; // Time to First Byte
}

/**
 * Hook to monitor page performance metrics
 * Tracks Core Web Vitals and reports to console (can be extended to analytics)
 */
export const usePagePerformance = (enableLogging: boolean = false) => {
  const location = useLocation();

  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') return;

    const metrics: PerformanceMetrics = {};

    // Observe paint timing (FCP)
    const paintObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          metrics.fcp = entry.startTime;
          if (enableLogging) {
            console.log(`[Performance] FCP: ${entry.startTime.toFixed(2)}ms`);
          }
        }
      }
    });

    try {
      paintObserver.observe({ entryTypes: ['paint'] });
    } catch (e) {
      // Paint timing not supported
    }

    // Observe Largest Contentful Paint (LCP)
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      metrics.lcp = lastEntry.startTime;
      if (enableLogging) {
        console.log(`[Performance] LCP: ${lastEntry.startTime.toFixed(2)}ms`);
      }
    });

    try {
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      // LCP not supported
    }

    // Observe First Input Delay (FID)
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        metrics.fid = (entry as any).processingStart - entry.startTime;
        if (enableLogging) {
          console.log(`[Performance] FID: ${metrics.fid?.toFixed(2)}ms`);
        }
      }
    });

    try {
      fidObserver.observe({ entryTypes: ['first-input'] });
    } catch (e) {
      // FID not supported
    }

    // Observe Cumulative Layout Shift (CLS)
    let clsValue = 0;
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
          metrics.cls = clsValue;
          if (enableLogging) {
            console.log(`[Performance] CLS: ${clsValue.toFixed(4)}`);
          }
        }
      }
    });

    try {
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      // CLS not supported
    }

    // Get Navigation Timing (TTFB)
    const navigationTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationTiming) {
      metrics.ttfb = navigationTiming.responseStart - navigationTiming.requestStart;
      if (enableLogging) {
        console.log(`[Performance] TTFB: ${metrics.ttfb.toFixed(2)}ms`);
      }
    }

    // Log route change timing
    const startTime = performance.now();
    if (enableLogging) {
      console.log(`[Performance] Route changed to: ${location.pathname}`);
    }

    // Cleanup
    return () => {
      const loadTime = performance.now() - startTime;
      if (enableLogging) {
        console.log(`[Performance] Page load time: ${loadTime.toFixed(2)}ms`);
      }

      paintObserver.disconnect();
      lcpObserver.disconnect();
      fidObserver.disconnect();
      clsObserver.disconnect();

      // Here you can send metrics to analytics service
      // Example: sendToAnalytics(metrics);
    };
  }, [location.pathname, enableLogging]);
};

/**
 * Report Web Vitals using web-vitals library (if installed)
 */
export const reportWebVitals = (onPerfEntry?: (metric: any) => void) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ onCLS, onINP, onFCP, onLCP, onTTFB }) => {
      onCLS(onPerfEntry);
      onINP(onPerfEntry);
      onFCP(onPerfEntry);
      onLCP(onPerfEntry);
      onTTFB(onPerfEntry);
    }).catch(() => {
      // web-vitals not installed, silently fail
    });
  }
};

export default usePagePerformance;
