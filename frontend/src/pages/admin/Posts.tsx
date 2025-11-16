import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { usePosts, useDeletePost, usePublishPost, useHidePost } from '../../hooks/usePosts';
import { Post } from '../../types';

const Posts: React.FC = () => {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<'draft' | 'published' | 'hidden' | undefined>();
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = usePosts({ page, status, search });
  const deletePost = useDeletePost();
  const publishPost = usePublishPost();
  const hidePost = useHidePost();

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      await deletePost.mutateAsync(id);
    }
  };

  const handlePublish = async (id: number) => {
    await publishPost.mutateAsync(id);
  };

  const handleHide = async (id: number) => {
    await hidePost.mutateAsync(id);
  };

  const getStatusBadge = (post: Post) => {
    const statusColors = {
      draft: 'bg-gray-200 text-gray-800',
      published: 'bg-green-200 text-green-800',
      hidden: 'bg-red-200 text-red-800',
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[post.status]}`}>
        {post.status}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-gray-600">Loading posts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-red-600">Error loading posts</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Posts</h1>
        <Link
          to="/admin/posts/new"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + New Post
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search posts..."
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={status || ''}
              onChange={(e) => setStatus(e.target.value as any || undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="hidden">Hidden</option>
            </select>
          </div>
        </div>
      </div>

      {/* Posts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Views
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Published
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data?.data.map((post) => (
              <tr key={post.id}>
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{post.title}</div>
                  <div className="text-sm text-gray-500 truncate max-w-xs">{post.excerpt}</div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {post.category?.name || '-'}
                </td>
                <td className="px-6 py-4">{getStatusBadge(post)}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{post.views}</td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {post.published_at
                    ? new Date(post.published_at).toLocaleDateString()
                    : '-'}
                </td>
                <td className="px-6 py-4 text-right text-sm space-x-2">
                  <Link
                    to={`/admin/posts/${post.id}/edit`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </Link>
                  {post.status === 'draft' && (
                    <button
                      onClick={() => handlePublish(post.id)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Publish
                    </button>
                  )}
                  {post.status === 'published' && (
                    <button
                      onClick={() => handleHide(post.id)}
                      className="text-yellow-600 hover:text-yellow-900"
                    >
                      Hide
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(post.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        {data?.meta && (
          <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Showing page {data.meta.page} of {data.meta.pages} ({data.meta.total} total)
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={!data.meta.has_prev}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.meta.has_next}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Posts;
