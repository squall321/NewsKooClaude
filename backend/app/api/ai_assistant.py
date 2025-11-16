"""
AI Assistant API

Draft 작성을 돕는 AI 보조 기능 엔드포인트:
- 여러 버전 생성
- 문단 개선
- 제목 생성
- 유사도 체크
- 피드백 기반 재작성
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from app import db
from app.models import User, Inspiration
from app.services.ai_rewriter import get_ai_rewriter, RewriteVersion
from app.utils.errors import ValidationError, NotFoundError
from app.utils.decorators import jwt_required_custom

ai_assistant_bp = Blueprint('ai_assistant', __name__)


@ai_assistant_bp.route('/generate-versions', methods=['POST'])
@jwt_required()
def generate_versions():
    """
    여러 버전의 재창작 콘텐츠 생성

    Request:
        {
            "concept": str,          # 원본 컨셉 (필수)
            "styles": [str],         # 스타일 목록 (선택, 기본: 3가지)
            "count": int            # 생성할 버전 수 (선택, 기본: 3, 최대: 7)
        }

    Response:
        {
            "message": str,
            "versions": [
                {
                    "style": str,
                    "content": str,
                    "similarity": float,
                    "is_fair_use": bool,
                    "metadata": dict
                }
            ]
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    concept = data.get('concept')
    if not concept or not concept.strip():
        raise ValidationError('Concept is required')

    # 선택 필드
    styles = data.get('styles')
    count = data.get('count', 3)

    # count 검증 (1-7)
    if not isinstance(count, int) or count < 1 or count > 7:
        raise ValidationError('Count must be between 1 and 7')

    # styles 검증
    if styles is not None:
        if not isinstance(styles, list):
            raise ValidationError('Styles must be a list')
        if len(styles) == 0:
            styles = None  # 빈 리스트면 None으로 처리 (기본값 사용)

    try:
        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        versions: List[RewriteVersion] = ai_rewriter.generate_multiple_versions(
            original_concept=concept,
            styles=styles,
            count=count
        )

        # 응답 변환
        versions_data = []
        for version in versions:
            versions_data.append({
                'style': version.style,
                'content': version.content,
                'similarity': version.similarity,
                'is_fair_use': version.is_fair_use,
                'metadata': version.metadata
            })

        return jsonify({
            'message': f'{len(versions_data)} versions generated successfully',
            'versions': versions_data
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to generate versions: {str(e)}')


@ai_assistant_bp.route('/improve-paragraph', methods=['POST'])
@jwt_required()
def improve_paragraph():
    """
    특정 문단 개선

    Request:
        {
            "paragraph": str,        # 개선할 문단 (필수)
            "goal": str,            # 개선 목표 (선택, 기본: "더 재미있게")
            "style": str            # 유머 스타일 (선택)
        }

    Response:
        {
            "message": str,
            "result": {
                "original": str,
                "improved": str,
                "goal": str,
                "style": str,
                "metadata": dict
            }
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    paragraph = data.get('paragraph')
    if not paragraph or not paragraph.strip():
        raise ValidationError('Paragraph is required')

    # 선택 필드
    goal = data.get('goal', '더 재미있게')
    style = data.get('style')

    try:
        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        result = ai_rewriter.improve_paragraph(
            paragraph=paragraph,
            improvement_goal=goal,
            style=style
        )

        return jsonify({
            'message': 'Paragraph improved successfully',
            'result': result
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to improve paragraph: {str(e)}')


@ai_assistant_bp.route('/generate-titles', methods=['POST'])
@jwt_required()
def generate_titles():
    """
    콘텐츠 기반 제목 생성

    Request:
        {
            "content": str,          # 콘텐츠 본문 (필수)
            "style": str,           # 제목 스타일 (선택, 기본: "catchy")
            "count": int            # 생성할 제목 수 (선택, 기본: 3, 최대: 5)
        }

    Response:
        {
            "message": str,
            "titles": [str],
            "style": str
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    content = data.get('content')
    if not content or not content.strip():
        raise ValidationError('Content is required')

    # 선택 필드
    style = data.get('style', 'catchy')
    count = data.get('count', 3)

    # count 검증 (1-5)
    if not isinstance(count, int) or count < 1 or count > 5:
        raise ValidationError('Count must be between 1 and 5')

    # style 검증
    valid_styles = ['catchy', 'informative', 'clickbait', 'simple', 'humorous']
    if style not in valid_styles:
        raise ValidationError(f'Style must be one of: {", ".join(valid_styles)}')

    try:
        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        titles = ai_rewriter.generate_title(
            content=content,
            style=style,
            count=count
        )

        return jsonify({
            'message': f'{len(titles)} titles generated successfully',
            'titles': titles,
            'style': style
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to generate titles: {str(e)}')


@ai_assistant_bp.route('/check-similarity', methods=['POST'])
@jwt_required()
def check_similarity():
    """
    Fair Use 준수 확인 (유사도 체크)

    Request:
        {
            "original": str,         # 원본 텍스트 (필수)
            "generated": str,        # 생성된 텍스트 (필수)
            "threshold": float      # Fair Use 임계값 (선택, 기본: 0.70)
        }

    Response:
        {
            "message": str,
            "result": {
                "is_fair_use": bool,
                "overall_similarity": float,
                "structural_similarity": float,
                "lexical_similarity": float,
                "semantic_similarity": float,
                "recommendation": str,
                "details": dict
            }
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    original = data.get('original')
    generated = data.get('generated')

    if not original or not original.strip():
        raise ValidationError('Original text is required')
    if not generated or not generated.strip():
        raise ValidationError('Generated text is required')

    # 선택 필드
    threshold = data.get('threshold', 0.70)

    # threshold 검증 (0.0-1.0)
    if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
        raise ValidationError('Threshold must be between 0.0 and 1.0')

    try:
        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        result = ai_rewriter.check_fair_use(
            original_text=original,
            generated_text=generated,
            threshold=threshold
        )

        # 메시지 생성
        if result['is_fair_use']:
            message = 'Fair Use check passed'
        else:
            message = 'Fair Use check failed - similarity too high'

        return jsonify({
            'message': message,
            'result': result
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to check similarity: {str(e)}')


@ai_assistant_bp.route('/rewrite-with-feedback', methods=['POST'])
@jwt_required()
def rewrite_with_feedback():
    """
    피드백 기반 재작성

    Request:
        {
            "concept": str,          # 원본 컨셉 (필수)
            "draft": str,           # 현재 초안 (필수)
            "feedback": str,        # 개선 피드백 (필수)
            "style": str            # 유머 스타일 (선택)
        }

    Response:
        {
            "message": str,
            "result": {
                "original_draft": str,
                "revised_draft": str,
                "feedback_applied": str,
                "similarity_to_original": float,
                "is_fair_use": bool,
                "metadata": dict
            }
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    concept = data.get('concept')
    draft = data.get('draft')
    feedback = data.get('feedback')

    if not concept or not concept.strip():
        raise ValidationError('Concept is required')
    if not draft or not draft.strip():
        raise ValidationError('Draft is required')
    if not feedback or not feedback.strip():
        raise ValidationError('Feedback is required')

    # 선택 필드
    style = data.get('style')

    try:
        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        result = ai_rewriter.rewrite_with_feedback(
            original_concept=concept,
            current_draft=draft,
            feedback=feedback,
            style=style
        )

        return jsonify({
            'message': 'Draft rewritten with feedback successfully',
            'result': result
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to rewrite with feedback: {str(e)}')


@ai_assistant_bp.route('/generate-from-inspiration/<int:inspiration_id>', methods=['POST'])
@jwt_required()
def generate_from_inspiration(inspiration_id: int):
    """
    Inspiration으로부터 여러 버전 생성

    Args:
        inspiration_id: Inspiration ID

    Request:
        {
            "styles": [str],         # 스타일 목록 (선택)
            "count": int            # 생성할 버전 수 (선택, 기본: 3)
        }

    Response:
        {
            "message": str,
            "inspiration": dict,
            "versions": [
                {
                    "style": str,
                    "content": str,
                    "similarity": float,
                    "is_fair_use": bool,
                    "metadata": dict
                }
            ]
        }
    """
    current_user_id = get_jwt_identity()

    # Inspiration 조회
    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    data = request.get_json() or {}

    # 선택 필드
    styles = data.get('styles')
    count = data.get('count', 3)

    # count 검증 (1-7)
    if not isinstance(count, int) or count < 1 or count > 7:
        raise ValidationError('Count must be between 1 and 7')

    try:
        # Inspiration의 concept 사용
        concept = inspiration.concept or inspiration.source.title

        # AI Rewriter 사용
        ai_rewriter = get_ai_rewriter()
        versions: List[RewriteVersion] = ai_rewriter.generate_multiple_versions(
            original_concept=concept,
            styles=styles,
            count=count
        )

        # 응답 변환
        versions_data = []
        for version in versions:
            versions_data.append({
                'style': version.style,
                'content': version.content,
                'similarity': version.similarity,
                'is_fair_use': version.is_fair_use,
                'metadata': version.metadata
            })

        return jsonify({
            'message': f'{len(versions_data)} versions generated from inspiration successfully',
            'inspiration': {
                'id': inspiration.id,
                'concept': concept,
                'source_title': inspiration.source.title if inspiration.source else None
            },
            'versions': versions_data
        }), 200

    except Exception as e:
        raise ValidationError(f'Failed to generate versions from inspiration: {str(e)}')


@ai_assistant_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    AI Assistant 사용 통계 조회

    Response:
        {
            "message": str,
            "statistics": {
                "available_styles": [str],
                "title_styles": [str],
                "default_fair_use_threshold": float,
                "max_versions": int,
                "max_titles": int
            }
        }
    """
    current_user_id = get_jwt_identity()

    # 사용 가능한 스타일 목록
    from app.llm.prompts import HumorStyle
    available_styles = [style.value for style in HumorStyle]

    title_styles = ['catchy', 'informative', 'clickbait', 'simple', 'humorous']

    statistics = {
        'available_styles': available_styles,
        'title_styles': title_styles,
        'default_fair_use_threshold': 0.70,
        'max_versions': 7,
        'max_titles': 5,
        'features': {
            'generate_versions': 'Generate multiple style versions from a concept',
            'improve_paragraph': 'Improve a specific paragraph',
            'generate_titles': 'Generate catchy titles',
            'check_similarity': 'Check Fair Use compliance',
            'rewrite_with_feedback': 'Rewrite based on feedback',
            'generate_from_inspiration': 'Generate versions from saved Inspiration'
        }
    }

    return jsonify({
        'message': 'AI Assistant statistics',
        'statistics': statistics
    }), 200
