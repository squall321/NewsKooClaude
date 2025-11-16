import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import Card from '../Card';

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <h1>Card Title</h1>
        <p>Card content</p>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies compact variant class', () => {
    const { container } = render(<Card compact>Content</Card>);
    expect(container.firstChild).toHaveClass('card-compact');
  });

  it('applies hoverable class', () => {
    const { container } = render(<Card hoverable>Content</Card>);
    expect(container.firstChild).toHaveClass('hoverable');
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('combines multiple props correctly', () => {
    const { container } = render(
      <Card compact hoverable className="extra-class">
        Content
      </Card>
    );

    const card = container.firstChild;
    expect(card).toHaveClass('card');
    expect(card).toHaveClass('card-compact');
    expect(card).toHaveClass('hoverable');
    expect(card).toHaveClass('extra-class');
  });
});
