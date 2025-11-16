import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';

// Layouts (not lazy - needed immediately)
import MainLayout from './components/layout/MainLayout';
import AdminLayout from './components/admin/AdminLayout';

// Loading fallback
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>
);

// Lazy-loaded Public Pages
const Home = lazy(() => import('./pages/Home'));
const PostDetail = lazy(() => import('./pages/PostDetail'));
const CategoryPage = lazy(() => import('./pages/CategoryPage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));

// Lazy-loaded Admin Pages
const Login = lazy(() => import('./pages/admin/Login'));
const Dashboard = lazy(() => import('./pages/admin/Dashboard'));
const Inspirations = lazy(() => import('./pages/admin/Inspirations'));
const Drafts = lazy(() => import('./pages/admin/Drafts'));
const Posts = lazy(() => import('./pages/admin/Posts'));
const Categories = lazy(() => import('./pages/admin/Categories'));
const Tags = lazy(() => import('./pages/admin/Tags'));
const WritingStyles = lazy(() => import('./pages/admin/WritingStyles'));
const Images = lazy(() => import('./pages/admin/Images'));
const Analytics = lazy(() => import('./pages/admin/Analytics'));

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
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <BrowserRouter>
            <AuthProvider>
              <Suspense fallback={<PageLoader />}>
              <Routes>
                {/* Public Routes */}
                <Route element={<MainLayout />}>
                  <Route path="/" element={<Home />} />
                  <Route path="/post/:slug" element={<PostDetail />} />
                  <Route path="/category/:slug" element={<CategoryPage />} />
                  <Route path="/search" element={<SearchPage />} />
                </Route>

                {/* Admin Login */}
                <Route path="/admin/login" element={<Login />} />

                {/* Protected Admin Routes */}
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
              </Suspense>
            </AuthProvider>
          </BrowserRouter>
        </ThemeProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
