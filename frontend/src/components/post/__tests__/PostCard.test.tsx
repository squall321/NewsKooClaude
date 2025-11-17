import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import PostCard from '../PostCard';
import type { Post } from '../../../types';

const mockPost: Post = {
  id: 1,
  title: 'Test Post Title',
  slug: 'test-post-title',
  content: 'This is test content',
  excerpt: 'This is a test excerpt',
  user_id: 1,
  category_id: 1,
  status: 'published',
  views: 100,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  published_at: '2025-01-01T00:00:00Z',
  featured_image: '/test-image.jpg',
  category: {
    id: 1,
    name: 'IT/Development',
    slug: 'it-development',
    description: 'IT and Development posts',
    created_at: '2025-01-01T00:00:00Z',
  },
  tags: [
    { id: 1, name: 'React', slug: 'react', created_at: '2025-01-01T00:00:00Z' },
    { id: 2, name: 'TypeScript', slug: 'typescript', created_at: '2025-01-01T00:00:00Z' },
  ],
};

describe('PostCard Component', () => {
  it('renders post title', () => {
    render(<PostCard post={mockPost} />);
    expect(screen.getByText('Test Post Title')).toBeInTheDocument();
  });

  it('renders post excerpt', () => {
    render(<PostCard post={mockPost} />);
    expect(screen.getByText('This is a test excerpt')).toBeInTheDocument();
  });

  it('renders category badge', () => {
    render(<PostCard post={mockPost} />);
    expect(screen.getByText('IT/Development')).toBeInTheDocument();
  });

  it('renders tags', () => {
    render(<PostCard post={mockPost} />);
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });

  it('displays view count', () => {
    render(<PostCard post={mockPost} />);
    expect(screen.getByText(/100/)).toBeInTheDocument();
  });

  it('renders featured image when provided', () => {
    render(<PostCard post={mockPost} />);
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', expect.stringContaining('test-image.jpg'));
  });

  it('links to post detail page', () => {
    render(<PostCard post={mockPost} />);
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/post/test-post-title');
  });

  it('renders without featured image', () => {
    const postWithoutImage = { ...mockPost, featured_image: null };
    render(<PostCard post={postWithoutImage} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('renders without tags', () => {
    const postWithoutTags = { ...mockPost, tags: [] };
    render(<PostCard post={postWithoutTags} />);
    expect(screen.queryByText('React')).not.toBeInTheDocument();
  });
});
