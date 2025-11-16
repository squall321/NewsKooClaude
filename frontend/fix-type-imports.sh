#!/bin/bash

# Fix type-only imports in TypeScript files

# Fix api/analytics.ts
sed -i "s/import { AnalyticsOverview, ContentStats }/import type { AnalyticsOverview, ContentStats }/" src/api/analytics.ts

# Fix api/categories.ts
sed -i "s/import { Category }/import type { Category }/" src/api/categories.ts

# Fix api/posts.ts
sed -i "s/import { Post, PaginatedResponse }/import type { Post, PaginatedResponse }/" src/api/posts.ts

# Fix api/tags.ts
sed -i "s/import { Tag }/import type { Tag }/" src/api/tags.ts

# Fix api/writingStyles.ts
sed -i "s/import { WritingStyle }/import type { WritingStyle }/" src/api/writingStyles.ts

echo "Type imports fixed successfully!"
