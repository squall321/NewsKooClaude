/**
 * 프론트엔드 성능 모니터링
 */

// 성능 메트릭 수집
export class PerformanceMonitor {
  /**
   * 페이지 로드 성능 측정
   */
  static getPageLoadMetrics() {
    if (typeof window === 'undefined' || !window.performance) {
      return null;
    }

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    if (!navigation) {
      return null;
    }

    return {
      // DNS 조회 시간
      dnsLookup: navigation.domainLookupEnd - navigation.domainLookupStart,

      // TCP 연결 시간
      tcpConnection: navigation.connectEnd - navigation.connectStart,

      // SSL/TLS 협상 시간
      tlsNegotiation:
        navigation.secureConnectionStart > 0
          ? navigation.connectEnd - navigation.secureConnectionStart
          : 0,

      // 요청 및 응답 시간
      requestTime: navigation.responseStart - navigation.requestStart,
      responseTime: navigation.responseEnd - navigation.responseStart,

      // DOM 처리 시간
      domProcessing: navigation.domComplete - navigation.domInteractive,

      // 전체 페이지 로드 시간
      totalLoadTime: navigation.loadEventEnd - navigation.fetchStart,

      // First Contentful Paint (FCP)
      firstContentfulPaint: this.getFirstContentfulPaint(),

      // Largest Contentful Paint (LCP)
      largestContentfulPaint: this.getLargestContentfulPaint(),

      // Time to Interactive (TTI)
      timeToInteractive: navigation.domInteractive - navigation.fetchStart,
    };
  }

  /**
   * First Contentful Paint 측정
   */
  private static getFirstContentfulPaint(): number | null {
    const entries = performance.getEntriesByName('first-contentful-paint');
    return entries.length > 0 ? entries[0].startTime : null;
  }

  /**
   * Largest Contentful Paint 측정
   */
  private static getLargestContentfulPaint(): number | null {
    let lcp: number | null = null;

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        lcp = lastEntry.renderTime || lastEntry.loadTime;
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      // LCP not supported
    }

    return lcp;
  }

  /**
   * 리소스 로딩 성능 측정
   */
  static getResourceMetrics() {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

    const byType = resources.reduce((acc, resource) => {
      const type = this.getResourceType(resource.name);

      if (!acc[type]) {
        acc[type] = {
          count: 0,
          totalSize: 0,
          totalDuration: 0,
        };
      }

      acc[type].count += 1;
      acc[type].totalSize += resource.transferSize || 0;
      acc[type].totalDuration += resource.duration;

      return acc;
    }, {} as Record<string, { count: number; totalSize: number; totalDuration: number }>);

    return byType;
  }

  /**
   * 리소스 타입 추출
   */
  private static getResourceType(url: string): string {
    if (url.match(/\.(js|mjs)$/)) return 'script';
    if (url.match(/\.(css)$/)) return 'stylesheet';
    if (url.match(/\.(png|jpg|jpeg|gif|webp|svg)$/)) return 'image';
    if (url.match(/\.(woff|woff2|ttf|eot)$/)) return 'font';
    if (url.includes('/api/')) return 'api';
    return 'other';
  }

  /**
   * 메모리 사용량 측정
   */
  static getMemoryMetrics() {
    if (typeof window === 'undefined' || !(performance as any).memory) {
      return null;
    }

    const memory = (performance as any).memory;

    return {
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      usedPercentage: ((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100).toFixed(2) + '%',
    };
  }

  /**
   * FPS (Frames Per Second) 측정
   */
  static measureFPS(duration: number = 1000): Promise<number> {
    return new Promise((resolve) => {
      let frames = 0;
      let lastTime = performance.now();

      const countFrames = (currentTime: number) => {
        frames++;

        if (currentTime - lastTime >= duration) {
          const fps = Math.round((frames * 1000) / (currentTime - lastTime));
          resolve(fps);
        } else {
          requestAnimationFrame(countFrames);
        }
      };

      requestAnimationFrame(countFrames);
    });
  }

  /**
   * Web Vitals 수집
   */
  static async getWebVitals() {
    try {
      const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals');

      const vitals: any = {};

      getCLS((metric) => (vitals.cls = metric.value));
      getFID((metric) => (vitals.fid = metric.value));
      getFCP((metric) => (vitals.fcp = metric.value));
      getLCP((metric) => (vitals.lcp = metric.value));
      getTTFB((metric) => (vitals.ttfb = metric.value));

      return vitals;
    } catch (e) {
      console.warn('web-vitals not available');
      return null;
    }
  }

  /**
   * 성능 보고서 생성
   */
  static generateReport() {
    return {
      timestamp: new Date().toISOString(),
      pageLoad: this.getPageLoadMetrics(),
      resources: this.getResourceMetrics(),
      memory: this.getMemoryMetrics(),
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
      connection: this.getConnectionInfo(),
    };
  }

  /**
   * 네트워크 연결 정보
   */
  private static getConnectionInfo() {
    const connection = (navigator as any).connection ||
                      (navigator as any).mozConnection ||
                      (navigator as any).webkitConnection;

    if (!connection) {
      return null;
    }

    return {
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData,
    };
  }
}

/**
 * 성능 측정 데코레이터
 */
export function measurePerformance(name: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const startTime = performance.now();

      try {
        const result = await originalMethod.apply(this, args);
        const duration = performance.now() - startTime;

        console.log(`[Performance] ${name} took ${duration.toFixed(2)}ms`);

        // 성능 마크 추가
        performance.mark(`${name}-end`);
        performance.measure(name, undefined, `${name}-end`);

        return result;
      } catch (error) {
        const duration = performance.now() - startTime;
        console.error(`[Performance] ${name} failed after ${duration.toFixed(2)}ms`);
        throw error;
      }
    };

    return descriptor;
  };
}

/**
 * React 컴포넌트 렌더링 성능 측정
 */
export function useRenderPerformance(componentName: string) {
  const renderCount = useRef(0);
  const renderTimes = useRef<number[]>([]);

  useEffect(() => {
    renderCount.current += 1;

    const renderTime = performance.now();
    renderTimes.current.push(renderTime);

    // 최근 10번의 렌더링 시간 유지
    if (renderTimes.current.length > 10) {
      renderTimes.current.shift();
    }

    // 평균 렌더링 시간 계산
    if (renderCount.current % 10 === 0) {
      const times = renderTimes.current;
      const avgTime = times.reduce((a, b, i) => {
        if (i === 0) return 0;
        return a + (times[i] - times[i - 1]);
      }, 0) / (times.length - 1);

      console.log(
        `[Performance] ${componentName} average render time: ${avgTime.toFixed(2)}ms ` +
        `(${renderCount.current} renders)`
      );
    }
  });

  return {
    renderCount: renderCount.current,
    avgRenderTime: renderTimes.current.length > 1
      ? renderTimes.current.reduce((a, b, i) => {
          if (i === 0) return 0;
          return a + (renderTimes.current[i] - renderTimes.current[i - 1]);
        }, 0) / (renderTimes.current.length - 1)
      : 0,
  };
}

// React imports
import { useEffect, useRef } from 'react';
