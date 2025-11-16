import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import Skeleton, { SkeletonCard, SkeletonPostCard } from '../Skeleton';

describe('Skeleton Component', () => {
  it('renders with default props', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveClass('skeleton');
  });

  it('renders different variants', () => {
    const { rerender, container } = render(<Skeleton variant="text" />);
    expect(container.firstChild).toHaveClass('skeleton-text');

    rerender(<Skeleton variant="title" />);
    expect(container.firstChild).toHaveClass('skeleton-title');

    rerender(<Skeleton variant="avatar" />);
    expect(container.firstChild).toHaveClass('skeleton-avatar');

    rerender(<Skeleton variant="rect" />);
    expect(container.firstChild).toHaveClass('skeleton-rect');
  });

  it('applies custom width and height', () => {
    const { container } = render(<Skeleton width="200px" height="100px" />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton.style.width).toBe('200px');
    expect(skeleton.style.height).toBe('100px');
  });

  it('applies custom className', () => {
    const { container } = render(<Skeleton className="custom-skeleton" />);
    expect(container.firstChild).toHaveClass('custom-skeleton');
  });
});

describe('SkeletonCard Component', () => {
  it('renders card skeleton', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('.skeleton-rect')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-title')).toBeInTheDocument();
    expect(container.querySelectorAll('.skeleton-text')).toHaveLength(2);
  });
});

describe('SkeletonPostCard Component', () => {
  it('renders post card skeleton', () => {
    const { container } = render(<SkeletonPostCard />);
    expect(container.querySelector('.skeleton-rect')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-title')).toBeInTheDocument();
    expect(container.querySelector('.skeleton-text')).toBeInTheDocument();
  });
});
