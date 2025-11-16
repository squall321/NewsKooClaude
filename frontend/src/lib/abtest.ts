/**
 * A/B 테스팅 클라이언트
 */

import axiosInstance from './axios';

interface VariantInfo {
  name: string;
  weight: number;
  [key: string]: any;
}

interface VariantData {
  test_name: string;
  variant: string;
  variant_info: VariantInfo;
}

// 변형 캐시
const variantCache = new Map<string, string>();

/**
 * A/B 테스트 변형 조회/할당
 */
export const getVariant = async (testName: string): Promise<string | null> => {
  // 캐시 확인
  if (variantCache.has(testName)) {
    return variantCache.get(testName)!;
  }

  try {
    const response = await axiosInstance.get<{ success: boolean; data: VariantData }>(
      `/api/ab-test/variant/${testName}`,
      {
        headers: {
          'X-Session-ID': getSessionId(),
        },
      }
    );

    if (response.data.success) {
      const variant = response.data.data.variant;
      variantCache.set(testName, variant);
      return variant;
    }

    return null;
  } catch (error) {
    console.error('Failed to get A/B test variant:', error);
    return null;
  }
};

/**
 * A/B 테스트 이벤트 추적
 */
export const trackABTestEvent = async (
  testName: string,
  eventType: string,
  value?: number,
  metadata?: any
) => {
  try {
    await axiosInstance.post(
      '/api/ab-test/event',
      {
        test_name: testName,
        event_type: eventType,
        value,
        metadata,
      },
      {
        headers: {
          'X-Session-ID': getSessionId(),
        },
      }
    );
  } catch (error) {
    console.error('Failed to track A/B test event:', error);
  }
};

/**
 * 세션 ID 가져오기
 */
const getSessionId = (): string => {
  let sessionId = localStorage.getItem('session_id');

  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('session_id', sessionId);
  }

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
 * A/B 테스트 Hook (React용)
 */
export const useABTest = (testName: string) => {
  const [variant, setVariant] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchVariant = async () => {
      const v = await getVariant(testName);
      setVariant(v);
      setIsLoading(false);
    };

    fetchVariant();
  }, [testName]);

  const trackEvent = (eventType: string, value?: number, metadata?: any) => {
    trackABTestEvent(testName, eventType, value, metadata);
  };

  return { variant, isLoading, trackEvent };
};

// React import for Hook
import { useState, useEffect } from 'react';
