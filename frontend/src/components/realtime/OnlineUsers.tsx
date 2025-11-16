/**
 * 온라인 사용자 수 표시 컴포넌트
 */

import React from 'react';
import { useSocket } from '../../hooks/useSocket';
import { Users } from 'lucide-react';

const OnlineUsers: React.FC = () => {
  const { onlineUsers, isConnected } = useSocket();

  if (!isConnected) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
      <div className="relative">
        <Users className="w-4 h-4" />
        {isConnected && (
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        )}
      </div>
      <span>{onlineUsers.toLocaleString()} 명 접속 중</span>
    </div>
  );
};

export default OnlineUsers;
