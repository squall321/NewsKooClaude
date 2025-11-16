/**
 * Google Analytics 4 Helper
 *
 * Usage:
 * 1. Add GA4 script to index.html
 * 2. Import and use gtag functions
 *
 * Example:
 * import { pageview, event } from './lib/analytics';
 * pageview('/post/my-article');
 * event('share', { method: 'twitter', content_type: 'post', item_id: 'post-123' });
 */

// Extend Window interface
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
    dataLayer?: any[];
  }
}

export const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // TODO: Replace with actual GA4 Measurement ID

/**
 * Initialize Google Analytics
 */
export const initGA = () => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('js', new Date());
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: window.location.pathname,
    });
  }
};

/**
 * Track page view
 */
export const pageview = (url: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }
};

/**
 * Track custom event
 */
export const event = (
  action: string,
  params?: {
    category?: string;
    label?: string;
    value?: number;
    [key: string]: any;
  }
) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, params);
  }
};

/**
 * Track search
 */
export const trackSearch = (searchTerm: string) => {
  event('search', {
    search_term: searchTerm,
  });
};

/**
 * Track share
 */
export const trackShare = (method: string, contentType: string, itemId: string) => {
  event('share', {
    method,
    content_type: contentType,
    item_id: itemId,
  });
};

/**
 * Track post view
 */
export const trackPostView = (postId: number, title: string, category?: string) => {
  event('view_item', {
    item_id: postId.toString(),
    item_name: title,
    item_category: category,
  });
};

/**
 * Track time on page
 */
export const trackTimeOnPage = (seconds: number) => {
  event('timing_complete', {
    name: 'page_engagement',
    value: seconds,
  });
};
