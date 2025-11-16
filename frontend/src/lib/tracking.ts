/**
 * 사용자 활동 추적 라이브러리
 */

import axiosInstance from './axios';

// 세션 ID 관리
let sessionId: string | null = null;

const getSessionId = (): string => {
  if (sessionId) {
    return sessionId;
  }

  // 로컬 스토리지에서 세션 ID 확인
  const stored = localStorage.getItem('session_id');
  if (stored) {
    sessionId = stored;
    return sessionId;
  }

  // 새 세션 ID 생성
  sessionId = generateUUID();
  localStorage.setItem('session_id', sessionId);
  return sessionId;
};

const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

/**
 * 활동 추적
 */
export const trackActivity = async (
  activityType: string,
  resourceType?: string,
  resourceId?: number,
  actionDetail?: any
) => {
  try {
    await axiosInstance.post(
      '/api/tracking/activity',
      {
        activity_type: activityType,
        resource_type: resourceType,
        resource_id: resourceId,
        action_detail: actionDetail,
      },
      {
        headers: {
          'X-Session-ID': getSessionId(),
        },
      }
    );
  } catch (error) {
    console.error('Activity tracking error:', error);
  }
};

/**
 * 페이지 조회 추적
 */
export const trackPageView = async (path: string, title?: string, duration?: number) => {
  try {
    const response = await axiosInstance.post(
      '/api/tracking/pageview',
      {
        path,
        title,
        duration,
      },
      {
        headers: {
          'X-Session-ID': getSessionId(),
        },
      }
    );

    if (response.data.session_id) {
      sessionId = response.data.session_id;
      localStorage.setItem('session_id', sessionId);
    }

    return response.data.pageview_id;
  } catch (error) {
    console.error('PageView tracking error:', error);
    return null;
  }
};

/**
 * 검색 로그 추적
 */
export const trackSearch = async (
  query: string,
  resultsCount?: number,
  filters?: any,
  clickedResultId?: number,
  clickedResultPosition?: number
) => {
  try {
    await axiosInstance.post(
      '/api/tracking/search',
      {
        query,
        results_count: resultsCount,
        filters,
        clicked_result_id: clickedResultId,
        clicked_result_position: clickedResultPosition,
      },
      {
        headers: {
          'X-Session-ID': getSessionId(),
        },
      }
    );
  } catch (error) {
    console.error('Search tracking error:', error);
  }
};

/**
 * 편의 함수들
 */
export const trackPostView = (postId: number) => {
  return trackActivity('view', 'post', postId);
};

export const trackPostLike = (postId: number) => {
  return trackActivity('like', 'post', postId);
};

export const trackPostShare = (postId: number, platform: string) => {
  return trackActivity('share', 'post', postId, { platform });
};

export const trackCommentPost = (postId: number, commentId: number) => {
  return trackActivity('comment', 'post', postId, { comment_id: commentId });
};

export const trackCategoryView = (categoryId: number) => {
  return trackActivity('view', 'category', categoryId);
};

export const trackTagClick = (tagName: string) => {
  return trackActivity('click', 'tag', undefined, { tag_name: tagName });
};

/**
 * 페이지 체류 시간 추적 Hook
 */
export class PageDurationTracker {
  private path: string;
  private title: string;
  private startTime: number;
  private pageviewId: number | null = null;
  private updateInterval: NodeJS.Timeout | null = null;

  constructor(path: string, title: string) {
    this.path = path;
    this.title = title;
    this.startTime = Date.now();
    this.init();
  }

  private async init() {
    // 초기 페이지뷰 기록
    this.pageviewId = await trackPageView(this.path, this.title);

    // 30초마다 체류 시간 업데이트
    this.updateInterval = setInterval(() => {
      this.update();
    }, 30000);

    // 페이지 언로드 시 최종 업데이트
    window.addEventListener('beforeunload', () => this.cleanup());
  }

  private async update() {
    const duration = Math.floor((Date.now() - this.startTime) / 1000);
    await trackPageView(this.path, this.title, duration);
  }

  public cleanup() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    // 최종 체류 시간 전송
    const duration = Math.floor((Date.now() - this.startTime) / 1000);

    // Beacon API 사용 (페이지 언로드 시에도 전송 보장)
    if (navigator.sendBeacon) {
      const blob = new Blob(
        [
          JSON.stringify({
            path: this.path,
            title: this.title,
            duration,
          }),
        ],
        { type: 'application/json' }
      );

      const apiUrl = axiosInstance.defaults.baseURL || '';
      navigator.sendBeacon(`${apiUrl}/api/tracking/pageview`, blob);
    } else {
      trackPageView(this.path, this.title, duration);
    }
  }
}
