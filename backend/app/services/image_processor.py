"""
이미지 업로드 및 처리 서비스

Draft 이미지 첨부를 위한 이미지 업로드, 리사이징, 최적화 기능을 제공합니다.
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class ImageProcessor:
    """
    이미지 업로드 및 처리 클래스

    Features:
    - 이미지 업로드 (PNG, JPG, JPEG, GIF, WEBP)
    - 이미지 리사이징 및 최적화
    - 썸네일 생성
    - 파일 검증
    """

    # 허용된 확장자
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # 최대 이미지 크기 (픽셀)
    MAX_IMAGE_WIDTH = 2000
    MAX_IMAGE_HEIGHT = 2000

    # 썸네일 크기
    THUMBNAIL_SIZE = (400, 400)

    # 이미지 품질
    QUALITY = 85

    def __init__(self, upload_folder: Path):
        """
        Args:
            upload_folder: 업로드 디렉토리 경로
        """
        self.upload_folder = Path(upload_folder)
        self._ensure_upload_folders()

    def _ensure_upload_folders(self):
        """업로드 디렉토리 생성"""
        # 메인 이미지 폴더
        self.images_folder = self.upload_folder / 'images'
        self.images_folder.mkdir(parents=True, exist_ok=True)

        # 썸네일 폴더
        self.thumbnails_folder = self.upload_folder / 'thumbnails'
        self.thumbnails_folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        파일 확장자 검증

        Args:
            filename: 파일명

        Returns:
            허용된 확장자 여부
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ImageProcessor.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_image(file: FileStorage) -> Tuple[bool, Optional[str]]:
        """
        이미지 파일 검증

        Args:
            file: 업로드된 파일 객체

        Returns:
            (성공 여부, 에러 메시지)
        """
        # 파일명 확인
        if not file or not file.filename:
            return False, 'No file provided'

        # 확장자 확인
        if not ImageProcessor.allowed_file(file.filename):
            return False, f'File type not allowed. Allowed types: {", ".join(ImageProcessor.ALLOWED_EXTENSIONS)}'

        # 이미지 파일인지 확인
        try:
            img = Image.open(file.stream)
            img.verify()
            file.stream.seek(0)  # Reset stream after verify
        except Exception as e:
            return False, f'Invalid image file: {str(e)}'

        return True, None

    def generate_filename(self, original_filename: str) -> str:
        """
        고유 파일명 생성

        Args:
            original_filename: 원본 파일명

        Returns:
            UUID + timestamp 기반 파일명
        """
        # 확장자 추출
        ext = original_filename.rsplit('.', 1)[1].lower()

        # UUID + timestamp로 고유 파일명 생성
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]

        return f"{timestamp}_{unique_id}.{ext}"

    def resize_image(self, image: Image.Image, max_width: int = None, max_height: int = None) -> Image.Image:
        """
        이미지 리사이징 (비율 유지)

        Args:
            image: PIL Image 객체
            max_width: 최대 너비
            max_height: 최대 높이

        Returns:
            리사이징된 이미지
        """
        max_width = max_width or self.MAX_IMAGE_WIDTH
        max_height = max_height or self.MAX_IMAGE_HEIGHT

        # 현재 크기
        width, height = image.size

        # 리사이징 필요 여부
        if width <= max_width and height <= max_height:
            return image

        # 비율 계산
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))

        # 리사이징
        return image.resize(new_size, Image.Resampling.LANCZOS)

    def create_thumbnail(self, image: Image.Image) -> Image.Image:
        """
        썸네일 생성 (정사각형 크롭)

        Args:
            image: PIL Image 객체

        Returns:
            썸네일 이미지
        """
        # 현재 크기
        width, height = image.size

        # 정사각형 크롭 (중앙)
        min_dimension = min(width, height)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension

        cropped = image.crop((left, top, right, bottom))

        # 썸네일 크기로 리사이징
        return cropped.resize(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

    def optimize_image(self, image: Image.Image) -> Image.Image:
        """
        이미지 최적화

        Args:
            image: PIL Image 객체

        Returns:
            최적화된 이미지
        """
        # RGBA -> RGB 변환 (JPEG는 투명도 지원 안 함)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            return background

        # RGB 변환
        if image.mode != 'RGB':
            return image.convert('RGB')

        return image

    def save_image(self, image: Image.Image, filename: str, folder: Path) -> str:
        """
        이미지 저장

        Args:
            image: PIL Image 객체
            filename: 저장할 파일명
            folder: 저장 폴더

        Returns:
            저장된 파일 경로
        """
        filepath = folder / filename

        # 확장자에 따라 포맷 결정
        ext = filename.rsplit('.', 1)[1].lower()

        if ext in ('jpg', 'jpeg'):
            image.save(filepath, 'JPEG', quality=self.QUALITY, optimize=True)
        elif ext == 'png':
            image.save(filepath, 'PNG', optimize=True)
        elif ext == 'webp':
            image.save(filepath, 'WEBP', quality=self.QUALITY)
        elif ext == 'gif':
            image.save(filepath, 'GIF', optimize=True)
        else:
            image.save(filepath, quality=self.QUALITY, optimize=True)

        return str(filepath)

    def upload_image(self, file: FileStorage, create_thumbnail: bool = True) -> dict:
        """
        이미지 업로드 및 처리

        Args:
            file: 업로드된 파일 객체
            create_thumbnail: 썸네일 생성 여부

        Returns:
            {
                'filename': str,  # 저장된 파일명
                'original_filename': str,  # 원본 파일명
                'url': str,  # 이미지 URL (상대 경로)
                'thumbnail_url': str,  # 썸네일 URL (상대 경로, 선택)
                'width': int,  # 이미지 너비
                'height': int,  # 이미지 높이
                'size': int  # 파일 크기 (bytes)
            }

        Raises:
            ValueError: 파일 검증 실패 시
        """
        # 파일 검증
        is_valid, error = self.validate_image(file)
        if not is_valid:
            raise ValueError(error)

        # 원본 파일명
        original_filename = secure_filename(file.filename)

        # 고유 파일명 생성
        filename = self.generate_filename(original_filename)

        # 이미지 열기
        image = Image.open(file.stream)

        # 이미지 최적화
        image = self.optimize_image(image)

        # 이미지 리사이징
        image = self.resize_image(image)

        # 메인 이미지 저장
        image_path = self.save_image(image, filename, self.images_folder)

        # 썸네일 생성 및 저장
        thumbnail_url = None
        if create_thumbnail:
            thumbnail = self.create_thumbnail(image)
            thumbnail_filename = f"thumb_{filename}"
            self.save_image(thumbnail, thumbnail_filename, self.thumbnails_folder)
            thumbnail_url = f"/uploads/thumbnails/{thumbnail_filename}"

        # 파일 크기
        file_size = os.path.getsize(image_path)

        return {
            'filename': filename,
            'original_filename': original_filename,
            'url': f"/uploads/images/{filename}",
            'thumbnail_url': thumbnail_url,
            'width': image.width,
            'height': image.height,
            'size': file_size
        }

    def delete_image(self, filename: str, delete_thumbnail: bool = True) -> bool:
        """
        이미지 삭제

        Args:
            filename: 파일명
            delete_thumbnail: 썸네일도 삭제 여부

        Returns:
            삭제 성공 여부
        """
        # 메인 이미지 삭제
        image_path = self.images_folder / filename
        if image_path.exists():
            image_path.unlink()

        # 썸네일 삭제
        if delete_thumbnail:
            thumbnail_path = self.thumbnails_folder / f"thumb_{filename}"
            if thumbnail_path.exists():
                thumbnail_path.unlink()

        return True

    def get_image_info(self, filename: str) -> Optional[dict]:
        """
        이미지 정보 조회

        Args:
            filename: 파일명

        Returns:
            이미지 정보 딕셔너리 또는 None
        """
        image_path = self.images_folder / filename

        if not image_path.exists():
            return None

        try:
            image = Image.open(image_path)
            file_size = os.path.getsize(image_path)

            # 썸네일 존재 여부
            thumbnail_path = self.thumbnails_folder / f"thumb_{filename}"
            thumbnail_url = f"/uploads/thumbnails/thumb_{filename}" if thumbnail_path.exists() else None

            return {
                'filename': filename,
                'url': f"/uploads/images/{filename}",
                'thumbnail_url': thumbnail_url,
                'width': image.width,
                'height': image.height,
                'size': file_size,
                'format': image.format
            }
        except Exception:
            return None
