import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './components/admin/AdminLayout';
import Login from './pages/admin/Login';
import Dashboard from './pages/admin/Dashboard';
import Inspirations from './pages/admin/Inspirations';
import Drafts from './pages/admin/Drafts';
import Posts from './pages/admin/Posts';
import Categories from './pages/admin/Categories';
import Tags from './pages/admin/Tags';
import WritingStyles from './pages/admin/WritingStyles';
import Images from './pages/admin/Images';
import Analytics from './pages/admin/Analytics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Redirect root to admin */}
            <Route path="/" element={<Navigate to="/admin" replace />} />

            {/* Login page */}
            <Route path="/admin/login" element={<Login />} />

            {/* Protected admin routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="inspirations" element={<Inspirations />} />
              <Route path="drafts" element={<Drafts />} />
              <Route path="posts" element={<Posts />} />
              <Route path="categories" element={<Categories />} />
              <Route path="tags" element={<Tags />} />
              <Route path="styles" element={<WritingStyles />} />
              <Route path="images" element={<Images />} />
              <Route
                path="analytics"
                element={
                  <ProtectedRoute requireRole="editor">
                    <Analytics />
                  </ProtectedRoute>
                }
              />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
