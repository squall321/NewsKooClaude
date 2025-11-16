import React from 'react';

export interface SkeletonProps {
  variant?: 'text' | 'title' | 'avatar' | 'rect';
  width?: string;
  height?: string;
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
}) => {
  const variantClass = variant !== 'rect' ? `skeleton-${variant}` : 'skeleton';
  const style = {
    ...(width && { width }),
    ...(height && { height }),
  };

  return (
    <div
      className={`${variantClass} ${className}`}
      style={style}
    />
  );
};

export const SkeletonCard: React.FC = () => {
  return (
    <div className="card animate-pulse">
      <Skeleton variant="title" />
      <Skeleton variant="text" />
      <Skeleton variant="text" />
      <Skeleton variant="text" width="60%" />
    </div>
  );
};

export const SkeletonPostCard: React.FC = () => {
  return (
    <div className="card animate-pulse">
      <Skeleton variant="rect" height="200px" className="mb-4" />
      <Skeleton variant="title" />
      <Skeleton variant="text" />
      <Skeleton variant="text" />
      <div className="flex items-center gap-3 mt-4">
        <Skeleton variant="avatar" />
        <div className="flex-1">
          <Skeleton variant="text" width="40%" />
          <Skeleton variant="text" width="30%" />
        </div>
      </div>
    </div>
  );
};

export default Skeleton;

/**
 * PostList Skeleton - 여러 개의 포스트 카드 skeleton
 */
export const PostListSkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonPostCard key={index} />
      ))}
    </div>
  );
};

/**
 * PostDetail Skeleton - 포스트 상세 페이지 skeleton
 */
export const PostDetailSkeleton: React.FC = () => {
  return (
    <div className="container-custom py-12 max-w-4xl">
      <Skeleton variant="title" className="mb-4" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="rect" height={400} className="mb-8" />
      <Skeleton variant="text" />
      <Skeleton variant="text" />
      <Skeleton variant="text" />
    </div>
  );
};
