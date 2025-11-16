/**
 * WebSocket Hook
 * React 컴포넌트에서 WebSocket을 쉽게 사용할 수 있는 Hook
 */

import { useEffect, useRef, useState } from 'react';
import { socketClient } from '../lib/socket';
import { useAuth } from './useAuth';

/**
 * WebSocket 연결 Hook
 */
export const useSocket = () => {
  const { token } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState(0);

  useEffect(() => {
    // 토큰이 있을 때만 연결
    if (token) {
      socketClient.connect(token);
      setIsConnected(socketClient.isConnected);
    }

    // 연결 상태 이벤트 리스너
    const handleConnect = () => setIsConnected(true);
    const handleDisconnect = () => setIsConnected(false);
    const handleOnlineUsers = (data: { count: number }) => {
      setOnlineUsers(data.count);
    };

    socketClient.on('connect', handleConnect);
    socketClient.on('disconnect', handleDisconnect);
    socketClient.on('online_users_count', handleOnlineUsers);

    return () => {
      socketClient.off('connect', handleConnect);
      socketClient.off('disconnect', handleDisconnect);
      socketClient.off('online_users_count', handleOnlineUsers);
    };
  }, [token]);

  return {
    isConnected,
    onlineUsers,
    socket: socketClient,
  };
};

/**
 * 게시물 실시간 업데이트 Hook
 */
export const usePostRealtime = (postId: number | null) => {
  const { socket } = useSocket();
  const [roomUsers, setRoomUsers] = useState(0);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!postId || !socket.isConnected) return;

    // 룸 참여
    socket.joinPost(postId);

    // 이벤트 리스너
    const handleRoomUsers = (data: { post_id: number; count: number }) => {
      if (data.post_id === postId) {
        setRoomUsers(data.count);
      }
    };

    const handleUserTyping = (data: { user_id: number; username: string; post_id: number }) => {
      if (data.post_id === postId) {
        setTypingUsers((prev) => new Set(prev).add(data.username));

        // 5초 후 자동 제거
        setTimeout(() => {
          setTypingUsers((prev) => {
            const newSet = new Set(prev);
            newSet.delete(data.username);
            return newSet;
          });
        }, 5000);
      }
    };

    const handleUserStopTyping = (data: { user_id: number; post_id: number }) => {
      if (data.post_id === postId) {
        // username을 받지 못하므로 전체 초기화 (또는 user_id 매핑 필요)
        setTypingUsers(new Set());
      }
    };

    socket.on('room_users_count', handleRoomUsers);
    socket.on('user_typing', handleUserTyping);
    socket.on('user_stop_typing', handleUserStopTyping);

    return () => {
      socket.off('room_users_count', handleRoomUsers);
      socket.off('user_typing', handleUserTyping);
      socket.off('user_stop_typing', handleUserStopTyping);

      // 룸 나가기
      socket.leavePost(postId);
    };
  }, [postId, socket]);

  return {
    roomUsers,
    typingUsers: Array.from(typingUsers),
  };
};

/**
 * 댓글 실시간 업데이트 Hook
 */
export const useCommentsRealtime = (
  postId: number | null,
  onNewComment?: (comment: any) => void,
  onCommentDeleted?: (commentId: number) => void
) => {
  const { socket } = useSocket();

  useEffect(() => {
    if (!postId || !socket.isConnected) return;

    const handleNewComment = (data: { post_id: number; comment: any }) => {
      if (data.post_id === postId && onNewComment) {
        onNewComment(data.comment);
      }
    };

    const handleCommentDeleted = (data: { post_id: number; comment_id: number }) => {
      if (data.post_id === postId && onCommentDeleted) {
        onCommentDeleted(data.comment_id);
      }
    };

    socket.on('new_comment', handleNewComment);
    socket.on('comment_deleted', handleCommentDeleted);

    return () => {
      socket.off('new_comment', handleNewComment);
      socket.off('comment_deleted', handleCommentDeleted);
    };
  }, [postId, socket, onNewComment, onCommentDeleted]);
};

/**
 * 게시물 좋아요/조회수 실시간 업데이트 Hook
 */
export const usePostStats = (
  postId: number | null,
  onLikesUpdate?: (likesCount: number) => void,
  onViewsUpdate?: (viewsCount: number) => void
) => {
  const { socket } = useSocket();

  useEffect(() => {
    if (!postId || !socket.isConnected) return;

    const handlePostLiked = (data: { post_id: number; likes_count: number }) => {
      if (data.post_id === postId && onLikesUpdate) {
        onLikesUpdate(data.likes_count);
      }
    };

    const handlePostViewed = (data: { post_id: number; views_count: number }) => {
      if (data.post_id === postId && onViewsUpdate) {
        onViewsUpdate(data.views_count);
      }
    };

    socket.on('post_liked', handlePostLiked);
    socket.on('post_viewed', handlePostViewed);

    return () => {
      socket.off('post_liked', handlePostLiked);
      socket.off('post_viewed', handlePostViewed);
    };
  }, [postId, socket, onLikesUpdate, onViewsUpdate]);
};

/**
 * 댓글 작성 중 표시 Hook
 */
export const useTypingIndicator = (postId: number | null) => {
  const { socket } = useSocket();
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const sendTyping = (username: string) => {
    if (!postId || !socket.isConnected) return;

    socket.sendTyping(postId, username);

    // 이전 타임아웃 클리어
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // 3초 후 자동으로 작성 중단 전송
    typingTimeoutRef.current = setTimeout(() => {
      sendStopTyping();
    }, 3000);
  };

  const sendStopTyping = () => {
    if (!postId || !socket.isConnected) return;

    socket.sendStopTyping(postId);

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      // 컴포넌트 언마운트 시 작성 중단 전송
      sendStopTyping();
    };
  }, []);

  return {
    sendTyping,
    sendStopTyping,
  };
};

/**
 * 알림 Hook
 */
export const useNotifications = (onNotification?: (notification: any) => void) => {
  const { socket } = useSocket();
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => {
    if (!socket.isConnected) return;

    const handleNotification = (notification: any) => {
      setNotifications((prev) => [notification, ...prev]);
      if (onNotification) {
        onNotification(notification);
      }
    };

    socket.on('notification', handleNotification);

    return () => {
      socket.off('notification', handleNotification);
    };
  }, [socket, onNotification]);

  const clearNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    clearNotifications,
  };
};
