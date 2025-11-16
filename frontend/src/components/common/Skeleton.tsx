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
