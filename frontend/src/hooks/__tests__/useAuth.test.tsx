import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuth } from '../useAuth';
import type { ReactNode } from 'react';

// Mock axios
vi.mock('../../lib/axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useAuth Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('initializes with no user when not authenticated', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('checks for existing token on mount', () => {
    localStorage.setItem('access_token', 'fake-token');

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isAuthenticated).toBe(true);
  });

  it('provides login function', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    expect(result.current.login).toBeDefined();
    expect(typeof result.current.login).toBe('function');
  });

  it('provides logout function', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    expect(result.current.logout).toBeDefined();
    expect(typeof result.current.logout).toBe('function');
  });

  it('clears token on logout', () => {
    localStorage.setItem('access_token', 'fake-token');

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    result.current.logout();

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
