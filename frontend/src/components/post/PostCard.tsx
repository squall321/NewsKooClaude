import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Post } from '../../types';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { staggerItem, imageFadeIn } from '../../lib/animations';

interface PostCardProps {
  post: Post;
}

const PostCard: React.FC<PostCardProps> = ({ post }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  return (
    <motion.div variants={staggerItem}>
      <Card hoverable className="group">
        <Link to={`/post/${post.slug}`} className="block">
          {/* Featured Image */}
          {post.featured_image && (
            <div className="relative overflow-hidden rounded-lg mb-4 aspect-video bg-gray-100">
              <motion.img
                src={post.featured_image}
                alt={post.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
                initial="initial"
                animate={imageLoaded ? 'animate' : 'initial'}
                variants={imageFadeIn}
                onLoad={() => setImageLoaded(true)}
              />
            </div>
          )}

        {/* Category Badge */}
        {post.category && (
          <Badge variant="primary" className="mb-2">
            {post.category.name}
          </Badge>
        )}

        {/* Title */}
        <h2 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
          {post.title}
        </h2>

        {/* Excerpt */}
        <p className="text-gray-600 mb-4 line-clamp-3">
          {post.excerpt}
        </p>

        {/* Meta Info */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{post.views}</span>
            </div>
            <span>{formatDate(post.published_at || post.created_at)}</span>
          </div>

          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex gap-2">
              {post.tags.slice(0, 2).map((tag) => (
                <span key={tag.id} className="text-xs text-gray-400">
                  #{tag.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </Link>
    </Card>
    </motion.div>
  );
};

export default PostCard;
