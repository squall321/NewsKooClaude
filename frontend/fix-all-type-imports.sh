#!/bin/bash

# Fix all remaining type-only import errors

# Components
sed -i "s/import { Post }/import type { Post }/" src/components/post/PostCard.tsx
sed -i "s/import { Post }/import type { Post }/" src/components/post/RelatedPosts.tsx
sed -i "s/import { Post }/import type { Post }/" src/components/widgets/PopularPosts.tsx
sed -i "s/import { Post }/import type { Post }/" src/components/widgets/RecentPosts.tsx

# Hooks
sed -i "s/import { Post }/import type { Post }/" src/hooks/usePosts.ts

# Contexts
sed -i "s/createContext, useState, useEffect, ReactNode/createContext, useState, useEffect/; s/} from 'react'/} from 'react';\nimport type { ReactNode } from 'react'/" src/contexts/AuthContext.tsx
sed -i "s/import { User, AuthResponse }/import type { User, AuthResponse }/" src/contexts/AuthContext.tsx
sed -i "s/createContext, useState, useEffect, ReactNode/createContext, useState, useEffect/; s/} from 'react'/} from 'react';\nimport type { ReactNode } from 'react'/" src/contexts/ThemeContext.tsx

# Lib
sed -i "s/import { Variants }/import type { Variants }/" src/lib/animations-enhanced.ts

# Toast
sed -i "s/, ReactNode } from 'react'/} from 'react';\nimport type { ReactNode } from 'react'/" src/components/common/Toast.tsx

echo "All type imports fixed!"
