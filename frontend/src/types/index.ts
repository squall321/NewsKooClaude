// Type definitions for NewsKoo platform

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'user' | 'editor' | 'admin';
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  post_count?: number;
  created_at: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  created_at: string;
}

export interface Source {
  id: number;
  platform: string;
  source_id: string;
  source_url: string;
  author_name?: string;
  subreddit?: string;
  upvotes: number;
  num_comments: number;
  collected_at: string;
}

export interface Inspiration {
  id: number;
  source_id: number;
  title: string;
  concept_summary: string;
  humor_type?: string;
  status: 'pending' | 'approved' | 'rejected' | 'used';
  similarity_score?: number;
  draft_id?: number;
  reviewed_at?: string;
  created_at: string;
  source?: Source;
}

export interface WritingStyle {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  tone: string;
  style_guide?: string;
  created_at: string;
}

export interface Draft {
  id: number;
  user_id: number;
  title: string;
  content: string;
  category_id?: number;
  inspiration_id?: number;
  writing_style_id?: number;
  featured_image?: string;
  ai_generated: boolean;
  similarity_score?: number;
  created_at: string;
  updated_at: string;
  category?: Category;
  tags?: Tag[];
}

export interface Post {
  id: number;
  user_id: number;
  draft_id?: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  featured_image?: string;
  category_id?: number;
  status: 'draft' | 'published' | 'hidden';
  published_at?: string;
  views: number;
  created_at: string;
  updated_at: string;
  category?: Category;
  tags?: Tag[];
  user?: User;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  user: User;
}

export interface ApiError {
  error: string;
  message: string;
  status_code: number;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface AnalyticsOverview {
  total_posts: number;
  published_posts: number;
  total_drafts: number;
  total_inspirations: number;
  total_users: number;
  total_sources: number;
}

export interface ContentStats {
  posts_by_period: Array<{ date: string; count: number }>;
  drafts_by_period: Array<{ date: string; count: number }>;
  by_category: Array<{ category: string; count: number }>;
  by_tag: Array<{ tag: string; count: number }>;
  ai_generated_percentage: number;
  manual_generated_percentage: number;
}
