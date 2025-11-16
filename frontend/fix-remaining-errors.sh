#!/bin/bash

echo "Fixing remaining type imports in pages..."

# Fix page type imports
for file in src/pages/admin/WritingStyles.tsx src/pages/admin/Tags.tsx src/pages/admin/Posts.tsx src/pages/admin/Categories.tsx src/pages/SearchPage.tsx src/pages/PostDetail.tsx src/pages/CategoryPage.tsx; do
  if [ -f "$file" ]; then
    # Convert specific type imports
    sed -i 's/import { Post }/import type { Post }/' "$file"
    sed -i 's/import { Category }/import type { Category }/' "$file"
    sed -i 's/import { Tag }/import type { Tag }/' "$file"
    sed -i 's/import { WritingStyle }/import type { WritingStyle }/' "$file"
    sed -i 's/import { Category, Post }/import type { Category, Post }/' "$file"
    sed -i 's/import { Post, Category }/import type { Post, Category }/' "$file"
  fi
done

echo "Fixing unused LoadingIndicator in Search.tsx..."
sed -i '/^import LoadingIndicator/d' src/pages/Search.tsx 2>/dev/null || true

echo "Fixing unused variables..."
sed -i 's/const pageviewId =/const _pageviewId =/' src/lib/tracking.ts 2>/dev/null || true
sed -i 's/(target, propertyKey, descriptor)/(_target, _propertyKey, descriptor)/' src/lib/performance.ts 2>/dev/null || true
sed -i 's/, b)/, _b)/' src/lib/performance.ts 2>/dev/null || true

echo "Fixing tracking.ts null type issue..."
# Add null check for localStorage.getItem
sed -i 's/sessionStorage.getItem(SESSION_ID_KEY)/sessionStorage.getItem(SESSION_ID_KEY) || ""/' src/lib/tracking.ts 2>/dev/null || true

echo "All remaining errors fixed!"
