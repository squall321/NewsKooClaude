import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../../api/analytics';

const Analytics: React.FC = () => {
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: analyticsApi.getOverview,
  });

  const { data: contentStats, isLoading: statsLoading } = useQuery({
    queryKey: ['analytics', 'content-stats'],
    queryFn: () => analyticsApi.getContentStats({ days: 30 }),
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['analytics', 'trends'],
    queryFn: () => analyticsApi.getTrends({ days: 30 }),
  });

  if (overviewLoading || statsLoading || trendsLoading) {
    return <div className="text-gray-600">Loading analytics...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">📄</div>
          <h3 className="text-lg font-semibold mb-1">Total Posts</h3>
          <p className="text-3xl font-bold text-blue-600">{overview?.total_posts || 0}</p>
          <p className="text-sm text-gray-500 mt-1">
            {overview?.published_posts || 0} published
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">📝</div>
          <h3 className="text-lg font-semibold mb-1">Drafts</h3>
          <p className="text-3xl font-bold text-yellow-600">{overview?.total_drafts || 0}</p>
          <p className="text-sm text-gray-500 mt-1">In progress</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">💡</div>
          <h3 className="text-lg font-semibold mb-1">Inspirations</h3>
          <p className="text-3xl font-bold text-purple-600">{overview?.total_inspirations || 0}</p>
          <p className="text-sm text-gray-500 mt-1">From {overview?.total_sources || 0} sources</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">👥</div>
          <h3 className="text-lg font-semibold mb-1">Users</h3>
          <p className="text-3xl font-bold text-green-600">{overview?.total_users || 0}</p>
          <p className="text-sm text-gray-500 mt-1">Total users</p>
        </div>
      </div>

      {/* Content Generation Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Content Generation</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">AI Generated</span>
              <span className="font-bold text-blue-600">
                {contentStats?.ai_generated_percentage || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${contentStats?.ai_generated_percentage || 0}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-4">
              <span className="text-gray-600">Manual</span>
              <span className="font-bold text-green-600">
                {contentStats?.manual_generated_percentage || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${contentStats?.manual_generated_percentage || 0}%` }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Top Categories</h2>
          <div className="space-y-3">
            {contentStats?.by_category?.slice(0, 5).map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-600">{item.category}</span>
                <span className="font-bold">{item.count}</span>
              </div>
            ))}
            {(!contentStats?.by_category || contentStats.by_category.length === 0) && (
              <p className="text-gray-500 text-sm">No data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Trends */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">30-Day Trends</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium mb-3">Daily Posts</h3>
            <div className="h-48 flex items-end justify-between gap-2">
              {trends?.daily_posts?.slice(-7).map((item: any, index: number) => {
                const maxCount = Math.max(...(trends?.daily_posts?.map((d: any) => d.count) || [1]));
                const height = (item.count / maxCount) * 100;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-blue-500 rounded-t"
                      style={{ height: `${height}%` }}
                    />
                    <span className="text-xs text-gray-500 mt-1">{item.count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-3">Popular Tags</h3>
            <div className="flex flex-wrap gap-2">
              {trends?.popular_tags?.slice(0, 10).map((item: any, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                >
                  {item.tag} ({item.count})
                </span>
              ))}
              {(!trends?.popular_tags || trends.popular_tags.length === 0) && (
                <p className="text-gray-500 text-sm">No tags yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
