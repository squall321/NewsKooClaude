import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface NavItem {
  path: string;
  label: string;
  icon: string;
  requireRole?: 'editor' | 'admin';
}

const navItems: NavItem[] = [
  { path: '/admin', label: 'Dashboard', icon: '📊' },
  { path: '/admin/inspirations', label: 'Inspirations', icon: '💡' },
  { path: '/admin/drafts', label: 'Drafts', icon: '📝' },
  { path: '/admin/posts', label: 'Posts', icon: '📄' },
  { path: '/admin/categories', label: 'Categories', icon: '📁' },
  { path: '/admin/tags', label: 'Tags', icon: '🏷️' },
  { path: '/admin/styles', label: 'Writing Styles', icon: '✍️' },
  { path: '/admin/images', label: 'Images', icon: '🖼️' },
  { path: '/admin/analytics', label: 'Analytics', icon: '📈', requireRole: 'editor' },
  { path: '/admin/users', label: 'Users', icon: '👥', requireRole: 'admin' },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const canAccess = (item: NavItem) => {
    if (!item.requireRole) return true;

    const roleHierarchy = { user: 0, editor: 1, admin: 2 };
    const userLevel = roleHierarchy[user?.role || 'user'];
    const requiredLevel = roleHierarchy[item.requireRole];

    return userLevel >= requiredLevel;
  };

  return (
    <aside className="w-64 bg-gray-800 text-white min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-2xl font-bold">NewsKoo</h1>
        <p className="text-sm text-gray-400">Admin Panel</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.filter(canAccess).map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-2 rounded transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
            <span className="text-lg">👤</span>
          </div>
          <div>
            <p className="font-medium">{user?.username}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors"
        >
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
