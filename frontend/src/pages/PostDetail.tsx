import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '../lib/axios';
import { Post } from '../types';
import Badge from '../components/common/Badge';
import Skeleton from '../components/common/Skeleton';
import RelatedPosts from '../components/post/RelatedPosts';

const PostDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  const { data: post, isLoading, error } = useQuery({
    queryKey: ['post', slug],
    queryFn: async () => {
      const response = await axiosInstance.get<Post>(`/api/posts/slug/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });

  // Increment view count
  useEffect(() => {
    if (post) {
      // Fire and forget - don't wait for response
      axiosInstance.post(`/api/posts/${post.id}/view`).catch(() => {
        // Silently fail if view count update fails
      });
    }
  }, [post]);

  if (isLoading) {
    return (
      <div className="container-custom py-12 max-w-4xl">
        <Skeleton variant="title" className="mb-4" />
        <Skeleton variant="text" className="mb-2" />
        <Skeleton variant="rect" height="400px" className="mb-8" />
        <Skeleton variant="text" />
        <Skeleton variant="text" />
        <Skeleton variant="text" />
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="container-custom py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Post not found</h2>
        <Link to="/" className="text-primary-600 hover:text-primary-700">
          Go back home
        </Link>
      </div>
    );
  }

  return (
    <article className="bg-white">
      {/* Header */}
      <header className="bg-gray-50 border-b border-gray-200">
        <div className="container-custom py-8 max-w-4xl">
          {post.category && (
            <Badge variant="primary" className="mb-4">
              {post.category.name}
            </Badge>
          )}
          <h1 className="text-4xl font-display font-bold text-gray-900 mb-4">
            {post.title}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>
              {new Date(post.published_at || post.created_at).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
            <span>•</span>
            <span>{post.views} views</span>
          </div>
        </div>
      </header>

      {/* Featured Image */}
      {post.featured_image && (
        <div className="container-custom py-8 max-w-4xl">
          <img
            src={post.featured_image}
            alt={post.title}
            className="w-full rounded-xl shadow-lg"
          />
        </div>
      )}

      {/* Content */}
      <div className="container-custom py-8 max-w-4xl">
        <div
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{ __html: post.content }}
        />

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t border-gray-200">
            {post.tags.map((tag) => (
              <Badge key={tag.id} variant="primary">
                #{tag.name}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Share & Back */}
      <div className="container-custom py-8 max-w-4xl border-t border-gray-200">
        <div className="flex items-center justify-between">
          <Link
            to="/"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            ← Back to Home
          </Link>
          <div className="flex gap-2">
            <button
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: post.title,
                    text: post.excerpt,
                    url: window.location.href,
                  });
                } else {
                  navigator.clipboard.writeText(window.location.href);
                  alert('Link copied to clipboard!');
                }
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Share"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </button>
            <button
              onClick={() => {
                const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}&url=${encodeURIComponent(window.location.href)}`;
                window.open(twitterUrl, '_blank');
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Share on Twitter"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Related Posts */}
      <div className="bg-gray-50 py-12">
        <div className="container-custom max-w-7xl">
          <RelatedPosts currentPostId={post.id} categoryId={post.category_id} />
        </div>
      </div>
    </article>
  );
};

export default PostDetail;
