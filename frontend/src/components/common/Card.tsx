import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  compact?: boolean;
  hoverable?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  compact = false,
  hoverable = false,
  onClick,
}) => {
  const baseClass = compact ? 'card-compact' : 'card';
  const hoverClass = hoverable ? 'cursor-pointer' : '';
  const clickableClass = onClick ? 'cursor-pointer' : '';

  return (
    <div
      className={`${baseClass} ${hoverClass} ${clickableClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;
