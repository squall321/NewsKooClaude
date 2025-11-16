/**
 * WebSocket 클라이언트
 * Socket.io를 사용한 실시간 통신
 */

import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class SocketClient {
  private socket: Socket | null = null;
  private token: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  /**
   * WebSocket 연결 초기화
   */
  connect(token?: string) {
    if (this.socket?.connected) {
      console.log('Socket already connected');
      return this.socket;
    }

    this.token = token || this.token;

    const options: any = {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
      timeout: 10000,
    };

    // 토큰이 있으면 쿼리 파라미터로 전달
    if (this.token) {
      options.query = { token: this.token };
    }

    this.socket = io(SOCKET_URL, options);

    this.setupEventHandlers();

    return this.socket;
  }

  /**
   * WebSocket 연결 해제
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  /**
   * 이벤트 핸들러 설정
   */
  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    // 온라인 사용자 수 업데이트
    this.socket.on('online_users_count', (data: { count: number }) => {
      console.log('Online users:', data.count);
      // 전역 상태 업데이트 (필요시)
    });
  }

  /**
   * 게시물 룸 참여
   */
  joinPost(postId: number) {
    if (!this.socket) {
      console.warn('Socket not connected');
      return;
    }

    this.socket.emit('join_post', { post_id: postId });
    console.log(`Joined post room: ${postId}`);
  }

  /**
   * 게시물 룸 나가기
   */
  leavePost(postId: number) {
    if (!this.socket) return;

    this.socket.emit('leave_post', { post_id: postId });
    console.log(`Left post room: ${postId}`);
  }

  /**
   * 댓글 작성 중 알림
   */
  sendTyping(postId: number, username: string) {
    if (!this.socket) return;

    this.socket.emit('typing', { post_id: postId, username });
  }

  /**
   * 댓글 작성 중단 알림
   */
  sendStopTyping(postId: number) {
    if (!this.socket) return;

    this.socket.emit('stop_typing', { post_id: postId });
  }

  /**
   * 이벤트 리스너 등록
   */
  on(event: string, callback: (...args: any[]) => void) {
    if (!this.socket) {
      console.warn('Socket not connected');
      return;
    }

    this.socket.on(event, callback);
  }

  /**
   * 이벤트 리스너 제거
   */
  off(event: string, callback?: (...args: any[]) => void) {
    if (!this.socket) return;

    if (callback) {
      this.socket.off(event, callback);
    } else {
      this.socket.off(event);
    }
  }

  /**
   * 이벤트 발생
   */
  emit(event: string, ...args: any[]) {
    if (!this.socket) {
      console.warn('Socket not connected');
      return;
    }

    this.socket.emit(event, ...args);
  }

  /**
   * 연결 상태 확인
   */
  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Socket 인스턴스 가져오기
   */
  getSocket(): Socket | null {
    return this.socket;
  }
}

// 싱글톤 인스턴스
export const socketClient = new SocketClient();

// 실시간 이벤트 타입
export interface NewCommentEvent {
  post_id: number;
  comment: {
    id: number;
    content: string;
    author: {
      id: number;
      username: string;
      avatar_url?: string;
    };
    created_at: string;
  };
}

export interface CommentDeletedEvent {
  post_id: number;
  comment_id: number;
}

export interface PostLikedEvent {
  post_id: number;
  likes_count: number;
}

export interface PostViewedEvent {
  post_id: number;
  views_count: number;
}

export interface UserTypingEvent {
  user_id: number;
  username: string;
  post_id: number;
}

export interface UserStopTypingEvent {
  user_id: number;
  post_id: number;
}

export interface RoomUsersCountEvent {
  post_id: number;
  count: number;
}

export interface OnlineUsersCountEvent {
  count: number;
}

export interface NotificationEvent {
  id: number;
  type: 'comment' | 'like' | 'mention' | 'follow';
  message: string;
  created_at: string;
  read: boolean;
  link?: string;
}
