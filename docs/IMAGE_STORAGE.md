# Image Storage Strategy

## Overview

NewsKoo supports multiple image storage backends with automatic optimization, thumbnail generation, and CDN integration.

## Table of Contents

1. [Storage Backends](#storage-backends)
2. [Configuration](#configuration)
3. [Image Upload API](#image-upload-api)
4. [Image Optimization](#image-optimization)
5. [CDN Integration](#cdn-integration)
6. [Backup Strategy](#backup-strategy)
7. [Best Practices](#best-practices)

---

## Storage Backends

### Supported Backends

1. **Local Storage** (Default)
   - Files stored on server filesystem
   - Best for: Development, small deployments
   - Pros: Simple, no external dependencies
   - Cons: No redundancy, limited scalability

2. **AWS S3**
   - Files stored on Amazon S3
   - Best for: Production, scalable deployments
   - Pros: Highly scalable, durable, CDN-ready
   - Cons: Costs money, requires AWS account

3. **CloudFlare R2**
   - S3-compatible storage with zero egress fees
   - Best for: Production with high traffic
   - Pros: No egress fees, fast global network
   - Cons: Requires CloudFlare account

### Storage Backend Comparison

| Feature | Local | S3 | R2 |
|---------|-------|----|----|
| **Cost** | Free | $$$ | $$ |
| **Scalability** | Low | High | High |
| **Durability** | Low | 99.999999999% | 99.999999999% |
| **Egress Fees** | N/A | Yes | No |
| **CDN Integration** | Manual | CloudFront | Automatic |
| **Backup** | Manual | Versioning | Versioning |

---

## Configuration

### Local Storage (Default)

```env
# .env.production
IMAGE_STORAGE_BACKEND=local
LOCAL_UPLOAD_DIR=/app/uploads
LOCAL_BASE_URL=/uploads
```

**Setup:**
```bash
# Create upload directory
mkdir -p /app/uploads
chmod 755 /app/uploads

# Configure Nginx to serve uploads
# Already configured in nginx/conf.d/default.conf
```

### AWS S3

```env
# .env.production
IMAGE_STORAGE_BACKEND=s3
S3_BUCKET=newskoo-images
S3_REGION=us-east-1
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_CDN_URL=https://cdn.newskoo.com
```

**Setup:**

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://newskoo-images --region us-east-1
   ```

2. **Configure Bucket Policy:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::newskoo-images/*"
       }
     ]
   }
   ```

3. **Enable CORS:**
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
       "AllowedOrigins": ["https://newskoo.com"],
       "ExposeHeaders": ["ETag"]
     }
   ]
   ```

4. **Create IAM User:**
   ```bash
   # Create user
   aws iam create-user --user-name newskoo-uploader

   # Attach policy
   aws iam attach-user-policy --user-name newskoo-uploader \
     --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

   # Create access key
   aws iam create-access-key --user-name newskoo-uploader
   ```

### CloudFlare R2

```env
# .env.production
IMAGE_STORAGE_BACKEND=r2
S3_BUCKET=newskoo-images
S3_REGION=auto
S3_ACCESS_KEY=your-r2-access-key
S3_SECRET_KEY=your-r2-secret-key
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
S3_CDN_URL=https://images.newskoo.com
```

**Setup:**

1. **Create R2 Bucket:**
   - Go to CloudFlare Dashboard → R2
   - Create bucket: `newskoo-images`
   - Enable public access

2. **Create API Token:**
   - R2 → Manage R2 API Tokens
   - Create token with "Object Read & Write" permissions
   - Copy Access Key ID and Secret Access Key

3. **Configure Custom Domain:**
   - R2 bucket → Settings → Public Access
   - Add custom domain: `images.newskoo.com`
   - Update DNS in CloudFlare

4. **CORS Configuration:**
   ```json
   [
     {
       "AllowedOrigins": ["https://newskoo.com"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
       "AllowedHeaders": ["*"],
       "ExposeHeaders": ["ETag"]
     }
   ]
   ```

---

## Image Upload API

### Upload Image

**Endpoint:** `POST /api/upload/image`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): Image file
- `folder` (optional): Folder/prefix (default: "images")
- `optimize` (optional): Optimize image (default: "true")
- `thumbnails` (optional): Generate thumbnails (default: "false")

**Example:**
```javascript
const formData = new FormData();
formData.append('file', imageFile);
formData.append('folder', 'posts');
formData.append('optimize', 'true');
formData.append('thumbnails', 'true');

const response = await axios.post('/api/upload/image', formData, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data',
  },
});

console.log(response.data);
// {
//   "success": true,
//   "data": {
//     "original": "https://cdn.newskoo.com/posts/abc123.jpg",
//     "thumbnails": {
//       "small": "https://cdn.newskoo.com/posts/abc123_small.jpg",
//       "medium": "https://cdn.newskoo.com/posts/abc123_medium.jpg",
//       "large": "https://cdn.newskoo.com/posts/abc123_large.jpg"
//     },
//     "width": 1920,
//     "height": 1080,
//     "format": "JPEG"
//   }
// }
```

### Upload Avatar

**Endpoint:** `POST /api/upload/avatar`

Automatically optimizes and generates thumbnails for user avatars.

**Example:**
```javascript
const formData = new FormData();
formData.append('file', avatarFile);

const response = await axios.post('/api/upload/avatar', formData, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data',
  },
});
```

### Upload Post Image

**Endpoint:** `POST /api/upload/post-image`

Optimized for post content images with responsive thumbnails.

### Delete Image

**Endpoint:** `DELETE /api/upload/image`

**Body:**
```json
{
  "url": "https://cdn.newskoo.com/posts/abc123.jpg"
}
```

---

## Image Optimization

### Automatic Optimization

Images are automatically optimized on upload:

1. **Format Conversion:**
   - RGBA/LA/P → RGB (with white background)
   - Preserves transparency where supported

2. **Size Reduction:**
   - Max dimension: 2048px
   - Maintains aspect ratio
   - Uses LANCZOS resampling

3. **Compression:**
   - JPEG: Quality 85 (configurable)
   - WebP: Quality 85 (configurable)
   - PNG: Optimized with compression

4. **Thumbnail Generation:**
   - Small: 150x150px
   - Medium: 300x300px
   - Large: 600x600px

### Batch Optimization

For existing images:

```bash
# Optimize all images in uploads directory
./scripts/image_optimize.sh /app/uploads

# This will:
# - Optimize JPEGs with jpegoptim
# - Optimize PNGs with optipng
# - Show before/after sizes
```

### Supported Formats

- **Input:** PNG, JPG, JPEG, GIF, WebP
- **Output:** PNG, JPG, WebP
- **Max Size:** 5MB (configurable)

---

## CDN Integration

### Why Use a CDN?

- **Performance:** Faster delivery from edge locations
- **Bandwidth:** Reduce origin server load
- **Scalability:** Handle traffic spikes
- **Security:** DDoS protection

### CloudFlare CDN (Recommended)

**Setup:**

1. **Add Custom Domain to R2:**
   - R2 bucket → Settings → Public Access
   - Connect custom domain: `images.newskoo.com`

2. **Configure DNS:**
   ```
   Type: CNAME
   Name: images
   Target: bucket.r2.cloudflarestorage.com
   Proxy: Enabled (orange cloud)
   ```

3. **Update Environment:**
   ```env
   S3_CDN_URL=https://images.newskoo.com
   ```

**Caching Rules:**

Go to CloudFlare → Caching → Cache Rules:

```
Cache images for 1 year:
  If hostname = images.newskoo.com
  AND URI path matches regex: .*\.(jpg|jpeg|png|gif|webp)$
  Then cache for 31536000 seconds
```

### AWS CloudFront

**Setup:**

1. **Create Distribution:**
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name newskoo-images.s3.us-east-1.amazonaws.com \
     --default-root-object index.html
   ```

2. **Configure Custom Domain:**
   - Add CNAME: `cdn.newskoo.com`
   - Add SSL certificate (ACM)

3. **Update Environment:**
   ```env
   S3_CDN_URL=https://cdn.newskoo.com
   ```

### Cache Headers

Images are served with appropriate cache headers:

```
Cache-Control: public, max-age=31536000, immutable
```

For local storage, configure Nginx:

```nginx
location /uploads {
    alias /app/uploads;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Backup Strategy

### Automated Backups

**Daily Backup Script:**

```bash
# Add to crontab
0 3 * * * /home/deploy/NewsKooClaude/scripts/image_backup.sh >> /home/deploy/logs/image_backup.log 2>&1
```

**What it does:**
- Creates compressed archive of all images
- Stores in `/home/deploy/backups/images`
- Cleans backups older than 90 days
- Optionally uploads to S3/R2

### Backup to Cloud

**AWS S3 Backup:**

```bash
#!/bin/bash
# Backup script with S3 upload

BACKUP_FILE="/home/deploy/backups/images/images_backup_$(date +%Y%m%d).tar.gz"

# Create backup
./scripts/image_backup.sh

# Upload to S3
aws s3 cp "$BACKUP_FILE" s3://newskoo-backups/images/

# Verify upload
aws s3 ls s3://newskoo-backups/images/ | grep "$(date +%Y%m%d)"
```

**CloudFlare R2 Backup:**

```bash
# Same as S3, R2 is S3-compatible
aws s3 cp "$BACKUP_FILE" s3://newskoo-backups/images/ \
  --endpoint-url https://your-account-id.r2.cloudflarestorage.com
```

### Restore from Backup

```bash
# Extract backup
tar -xzf /path/to/images_backup_20250116.tar.gz -C /tmp/

# Copy to upload directory
cp -r /tmp/uploads/* /app/uploads/

# Fix permissions
chmod -R 755 /app/uploads
```

### S3 Versioning

For S3/R2, enable versioning for automatic backups:

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket newskoo-images \
  --versioning-configuration Status=Enabled

# List versions
aws s3api list-object-versions --bucket newskoo-images
```

---

## Best Practices

### 1. Storage Selection

**Development:**
- Use local storage for simplicity
- No external dependencies
- Easy debugging

**Production (Low Traffic):**
- AWS S3 with CloudFront
- Proven reliability
- Pay for what you use

**Production (High Traffic):**
- CloudFlare R2
- Zero egress fees
- Built-in CDN
- Best for image-heavy sites

### 2. Image Optimization

**Always optimize images:**
```javascript
// In frontend upload component
const optimizeImage = async (file) => {
  // Let backend handle optimization
  formData.append('optimize', 'true');
  formData.append('thumbnails', 'true');
};
```

**Use WebP when possible:**
```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Fallback">
</picture>
```

### 3. Responsive Images

**Use thumbnails for lists:**
```jsx
// PostCard component
<img
  src={post.thumbnail_url || post.image_url}
  alt={post.title}
  loading="lazy"
/>
```

**Use srcset for different screen sizes:**
```html
<img
  src="image_medium.jpg"
  srcset="image_small.jpg 150w,
          image_medium.jpg 300w,
          image_large.jpg 600w"
  sizes="(max-width: 600px) 150px,
         (max-width: 1200px) 300px,
         600px"
  alt="Responsive image"
/>
```

### 4. Security

**Validate uploads:**
- File type validation (server-side)
- File size limits
- Sanitize filenames
- Scan for malware (optional)

**Access control:**
- Public images: No authentication
- User avatars: Restrict to user
- Private images: Use signed URLs

### 5. Performance

**Lazy loading:**
```html
<img src="image.jpg" loading="lazy" alt="Lazy loaded">
```

**Preload critical images:**
```html
<link rel="preload" as="image" href="hero-image.jpg">
```

**Use CDN:**
- Reduces latency
- Improves page load time
- Better user experience

### 6. Cost Optimization

**S3 Cost Reduction:**
- Use Intelligent-Tiering for old images
- Set lifecycle policies
- Delete unused images

**R2 Benefits:**
- No egress fees (major savings)
- Lower storage costs than S3
- Free bandwidth

**Storage Cleanup:**
```sql
-- Find unused images
SELECT url FROM images
WHERE created_at < NOW() - INTERVAL '1 year'
  AND referenced_count = 0;
```

---

## Migration Guide

### Local → S3

1. **Upload existing images to S3:**
   ```bash
   aws s3 sync /app/uploads s3://newskoo-images/
   ```

2. **Update environment:**
   ```env
   IMAGE_STORAGE_BACKEND=s3
   ```

3. **Update database URLs:**
   ```sql
   UPDATE posts
   SET image_url = REPLACE(image_url, '/uploads/', 'https://newskoo-images.s3.amazonaws.com/')
   WHERE image_url LIKE '/uploads/%';
   ```

4. **Restart application**

### S3 → R2

1. **Create R2 bucket**

2. **Copy from S3 to R2:**
   ```bash
   # Using rclone
   rclone copy s3:newskoo-images r2:newskoo-images
   ```

3. **Update environment:**
   ```env
   IMAGE_STORAGE_BACKEND=r2
   S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
   ```

4. **Update database URLs**

---

## Troubleshooting

### Upload Fails

**Check file size:**
```python
# Increase max size in config
MAX_IMAGE_SIZE=10485760  # 10MB
```

**Check permissions:**
```bash
chmod 755 /app/uploads
chown -R www-data:www-data /app/uploads
```

### S3/R2 Connection Fails

**Verify credentials:**
```bash
aws s3 ls s3://newskoo-images --endpoint-url $S3_ENDPOINT_URL
```

**Check CORS:**
```bash
aws s3api get-bucket-cors --bucket newskoo-images
```

### Images Not Loading

**Check CDN URL:**
```bash
curl -I https://cdn.newskoo.com/images/test.jpg
```

**Check bucket policy:**
```bash
aws s3api get-bucket-policy --bucket newskoo-images
```

---

## Quick Reference

```bash
# Upload image via API
curl -X POST https://newskoo.com/api/upload/image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.jpg" \
  -F "optimize=true" \
  -F "thumbnails=true"

# Backup images
./scripts/image_backup.sh

# Optimize existing images
./scripts/image_optimize.sh /app/uploads

# Sync to S3
aws s3 sync /app/uploads s3://newskoo-images/

# List S3 files
aws s3 ls s3://newskoo-images/ --recursive
```

---

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [CloudFlare R2 Documentation](https://developers.cloudflare.com/r2/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Image Optimization Guide](https://web.dev/fast/#optimize-your-images)
