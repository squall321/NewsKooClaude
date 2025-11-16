"""
Image Upload API
Handles image uploads with optimization and thumbnail generation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.image_storage import image_storage


upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """
    Upload image

    Request:
        - file: Image file (multipart/form-data)
        - folder: Optional folder name (default: 'images')
        - optimize: Optional, whether to optimize image (default: true)
        - thumbnails: Optional, whether to generate thumbnails (default: false)

    Response:
        {
            "success": true,
            "data": {
                "original": "https://...",
                "thumbnails": {
                    "small": "https://...",
                    "medium": "https://...",
                    "large": "https://..."
                },
                "width": 1920,
                "height": 1080,
                "format": "JPEG"
            }
        }
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Get options
        folder = request.form.get('folder', 'images')
        optimize = request.form.get('optimize', 'true').lower() == 'true'
        generate_thumbnails = request.form.get('thumbnails', 'false').lower() == 'true'

        # Upload image
        result = image_storage.save(
            file=file,
            folder=folder,
            optimize=optimize,
            generate_thumbnails=generate_thumbnails
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to upload image'
        }), 500


@upload_bp.route('/image', methods=['DELETE'])
@jwt_required()
def delete_image():
    """
    Delete image

    Request:
        {
            "url": "https://..."
        }

    Response:
        {
            "success": true
        }
    """
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        # Delete image
        success = image_storage.delete(url)

        if success:
            return jsonify({
                'success': True
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete image'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete image'
        }), 500


@upload_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """
    Upload user avatar
    Automatically optimizes and generates thumbnails
    """
    try:
        current_user_id = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        # Upload with avatar-specific settings
        result = image_storage.save(
            file=file,
            folder=f'avatars/{current_user_id}',
            optimize=True,
            generate_thumbnails=True
        )

        # TODO: Update user avatar in database
        # from app.models import User
        # user = User.query.get(current_user_id)
        # user.avatar_url = result['original']
        # user.avatar_thumbnail = result['thumbnails']['medium']
        # db.session.commit()

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to upload avatar'
        }), 500


@upload_bp.route('/post-image', methods=['POST'])
@jwt_required()
def upload_post_image():
    """
    Upload image for post content
    Optimizes and generates thumbnails for responsive display
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        # Upload with post-specific settings
        result = image_storage.save(
            file=file,
            folder='posts',
            optimize=True,
            generate_thumbnails=True
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to upload post image'
        }), 500
