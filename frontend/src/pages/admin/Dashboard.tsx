import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Welcome, {user?.username}!</h2>
        <p className="text-gray-600">
          Role: <span className="font-medium capitalize">{user?.role}</span>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">📝</div>
          <h3 className="text-lg font-semibold mb-1">Drafts</h3>
          <p className="text-gray-600">Manage your drafts</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">📄</div>
          <h3 className="text-lg font-semibold mb-1">Posts</h3>
          <p className="text-gray-600">Published content</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">💡</div>
          <h3 className="text-lg font-semibold mb-1">Inspirations</h3>
          <p className="text-gray-600">Content ideas</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl mb-2">📊</div>
          <h3 className="text-lg font-semibold mb-1">Analytics</h3>
          <p className="text-gray-600">View statistics</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
