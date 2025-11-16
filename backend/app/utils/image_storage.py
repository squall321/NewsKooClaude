"""
Image Storage Utility
Supports multiple storage backends: Local, S3, CloudFlare R2
"""

import os
import hashlib
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class ImageStorageConfig:
    """Configuration for image storage"""

    # Storage backend: 'local', 's3', 'r2'
    BACKEND = os.getenv('IMAGE_STORAGE_BACKEND', 'local')

    # Local storage
    LOCAL_UPLOAD_DIR = os.getenv('LOCAL_UPLOAD_DIR', '/app/uploads')
    LOCAL_BASE_URL = os.getenv('LOCAL_BASE_URL', '/uploads')

    # S3 / R2 configuration
    S3_BUCKET = os.getenv('S3_BUCKET', '')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', None)  # For CloudFlare R2
    S3_CDN_URL = os.getenv('S3_CDN_URL', '')  # Custom domain for CDN

    # Image optimization
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 5 * 1024 * 1024))  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Thumbnail sizes
    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (600, 600),
    }

    # Image quality
    JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', 85))
    WEBP_QUALITY = int(os.getenv('WEBP_QUALITY', 85))


class ImageStorage:
    """Image storage handler"""

    def __init__(self):
        self.config = ImageStorageConfig()
        self.backend = self._get_backend()

    def _get_backend(self):
        """Get storage backend based on configuration"""
        if self.config.BACKEND == 's3' or self.config.BACKEND == 'r2':
            return S3Storage(self.config)
        else:
            return LocalStorage(self.config)

    def save(
        self,
        file: FileStorage,
        folder: str = 'images',
        optimize: bool = True,
        generate_thumbnails: bool = False
    ) -> dict:
        """
        Save image file

        Args:
            file: Uploaded file
            folder: Storage folder/prefix
            optimize: Whether to optimize image
            generate_thumbnails: Whether to generate thumbnails

        Returns:
            dict with image URLs and metadata
        """
        # Validate file
        if not self.validate_file(file):
            raise ValueError('Invalid file type or size')

        # Generate unique filename
        filename = self._generate_filename(file.filename)

        # Process image
        image = Image.open(file.stream)

        if optimize:
            image = self._optimize_image(image)

        # Save original
        image_buffer = self._image_to_buffer(image, filename)
        original_url = self.backend.upload(image_buffer, folder, filename)

        result = {
            'original': original_url,
            'thumbnails': {},
            'width': image.width,
            'height': image.height,
            'format': image.format,
        }

        # Generate thumbnails
        if generate_thumbnails:
            for size_name, size in self.config.THUMBNAIL_SIZES.items():
                thumb = self._create_thumbnail(image, size)
                thumb_filename = f"{os.path.splitext(filename)[0]}_{size_name}{os.path.splitext(filename)[1]}"
                thumb_buffer = self._image_to_buffer(thumb, thumb_filename)
                thumb_url = self.backend.upload(thumb_buffer, folder, thumb_filename)
                result['thumbnails'][size_name] = thumb_url

        return result

    def delete(self, url: str) -> bool:
        """Delete image from storage"""
        return self.backend.delete(url)

    def validate_file(self, file: FileStorage) -> bool:
        """Validate uploaded file"""
        if not file or not file.filename:
            return False

        # Check extension
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in self.config.ALLOWED_EXTENSIONS:
            return False

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > self.config.MAX_IMAGE_SIZE:
            return False

        return True

    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename"""
        import time

        filename = secure_filename(original_filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'

        # Create hash from timestamp and original name
        timestamp = str(time.time()).encode('utf-8')
        name_hash = hashlib.md5(timestamp + filename.encode('utf-8')).hexdigest()[:12]

        return f"{name_hash}.{ext}"

    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """Optimize image (convert to RGB, resize if too large)"""
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if too large (max 2048px on longest side)
        max_dimension = 2048
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _create_thumbnail(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Create thumbnail with aspect ratio preserved"""
        thumb = image.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        return thumb

    def _image_to_buffer(self, image: Image.Image, filename: str) -> BytesIO:
        """Convert PIL Image to BytesIO buffer"""
        buffer = BytesIO()

        # Determine format from filename
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'

        if ext == 'png':
            image.save(buffer, format='PNG', optimize=True)
        elif ext == 'webp':
            image.save(buffer, format='WEBP', quality=self.config.WEBP_QUALITY, optimize=True)
        else:
            image.save(buffer, format='JPEG', quality=self.config.JPEG_QUALITY, optimize=True)

        buffer.seek(0)
        return buffer


class LocalStorage:
    """Local filesystem storage backend"""

    def __init__(self, config: ImageStorageConfig):
        self.config = config
        os.makedirs(config.LOCAL_UPLOAD_DIR, exist_ok=True)

    def upload(self, file_buffer: BytesIO, folder: str, filename: str) -> str:
        """Upload file to local storage"""
        # Create folder if not exists
        folder_path = os.path.join(self.config.LOCAL_UPLOAD_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)

        # Save file
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_buffer.read())

        # Return URL
        return f"{self.config.LOCAL_BASE_URL}/{folder}/{filename}"

    def delete(self, url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract path from URL
            path = url.replace(self.config.LOCAL_BASE_URL, self.config.LOCAL_UPLOAD_DIR)
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception:
            pass
        return False


class S3Storage:
    """S3/R2 storage backend"""

    def __init__(self, config: ImageStorageConfig):
        self.config = config
        self.client = self._get_client()

    def _get_client(self):
        """Initialize S3/R2 client"""
        try:
            import boto3

            session = boto3.session.Session()

            client_config = {
                'aws_access_key_id': self.config.S3_ACCESS_KEY,
                'aws_secret_access_key': self.config.S3_SECRET_KEY,
                'region_name': self.config.S3_REGION,
            }

            # For CloudFlare R2, use custom endpoint
            if self.config.S3_ENDPOINT_URL:
                client_config['endpoint_url'] = self.config.S3_ENDPOINT_URL

            return session.client('s3', **client_config)
        except ImportError:
            raise ImportError('boto3 is required for S3/R2 storage. Install with: pip install boto3')

    def upload(self, file_buffer: BytesIO, folder: str, filename: str) -> str:
        """Upload file to S3/R2"""
        key = f"{folder}/{filename}"

        # Determine content type
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')

        # Upload to S3/R2
        self.client.put_object(
            Bucket=self.config.S3_BUCKET,
            Key=key,
            Body=file_buffer,
            ContentType=content_type,
            ACL='public-read',
        )

        # Return URL (use CDN if configured)
        if self.config.S3_CDN_URL:
            return f"{self.config.S3_CDN_URL}/{key}"
        else:
            return f"https://{self.config.S3_BUCKET}.s3.{self.config.S3_REGION}.amazonaws.com/{key}"

    def delete(self, url: str) -> bool:
        """Delete file from S3/R2"""
        try:
            # Extract key from URL
            if self.config.S3_CDN_URL and url.startswith(self.config.S3_CDN_URL):
                key = url.replace(self.config.S3_CDN_URL + '/', '')
            else:
                # Extract from S3 URL
                key = url.split(self.config.S3_BUCKET + '/')[-1]

            self.client.delete_object(
                Bucket=self.config.S3_BUCKET,
                Key=key,
            )
            return True
        except Exception:
            return False


# Singleton instance
image_storage = ImageStorage()
