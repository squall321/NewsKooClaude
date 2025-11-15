"""
에러 핸들링 유틸리티
커스텀 예외 및 전역 에러 핸들러
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """기본 API 에러 클래스"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """에러를 딕셔너리로 변환"""
        rv = dict(self.payload or ())
        rv['error'] = True
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """데이터 검증 에러 (400)"""
    status_code = 400


class AuthenticationError(APIError):
    """인증 에러 (401)"""
    status_code = 401


class AuthorizationError(APIError):
    """권한 에러 (403)"""
    status_code = 403


class NotFoundError(APIError):
    """리소스 없음 에러 (404)"""
    status_code = 404


class ConflictError(APIError):
    """충돌 에러 (409) - 예: 중복된 데이터"""
    status_code = 409


def register_error_handlers(app):
    """
    전역 에러 핸들러 등록

    Args:
        app: Flask 애플리케이션
    """

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """커스텀 API 에러 핸들러"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Werkzeug HTTP 예외 핸들러"""
        response = jsonify({
            'error': True,
            'message': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        """404 Not Found 핸들러"""
        return jsonify({
            'error': True,
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404

    @app.errorhandler(500)
    def handle_500(error):
        """500 Internal Server Error 핸들러"""
        # 프로덕션 환경에서는 에러 상세 정보를 노출하지 않음
        return jsonify({
            'error': True,
            'message': 'An internal server error occurred',
            'status_code': 500
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """예상치 못한 에러 핸들러"""
        app.logger.error(f'Unexpected error: {str(error)}', exc_info=True)
        return jsonify({
            'error': True,
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
