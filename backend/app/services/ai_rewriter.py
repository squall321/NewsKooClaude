"""
AI 재작성 서비스

AI를 활용하여 콘텐츠를 재작성하고 개선하는 서비스입니다.
- 여러 버전 생성 (다양한 스타일)
- 문단 개선 (특정 부분만 리라이트)
- 제목 생성 (콘텐츠 기반)
- 유사도 체크 (Fair Use 준수)
"""
from typing import List, Optional, Dict
from dataclasses import dataclass

from app.llm.model_loader import get_llm_instance
from app.llm.prompts import HumorStyle, build_full_prompt
from app.services.content_generator import ContentGenerator, GenerationResult
from app.services.similarity_checker import SimilarityChecker, SimilarityResult


@dataclass
class RewriteVersion:
    """재작성 버전 데이터 클래스"""
    style: str
    content: str
    similarity: float
    is_fair_use: bool
    metadata: Dict


class AIRewriter:
    """
    AI 재작성 서비스

    ContentGenerator와 SimilarityChecker를 활용하여
    다양한 AI 보조 작성 기능을 제공합니다.
    """

    def __init__(self):
        """AIRewriter 초기화"""
        self.llm = get_llm_instance()
        self.content_generator = ContentGenerator()
        self.similarity_checker = SimilarityChecker()

    def generate_multiple_versions(
        self,
        original_concept: str,
        styles: Optional[List[str]] = None,
        count: int = 3
    ) -> List[RewriteVersion]:
        """
        여러 버전의 재창작 콘텐츠 생성

        동일한 컨셉으로 여러 스타일의 콘텐츠를 생성합니다.

        Args:
            original_concept: 원본 컨셉 (원문이 아닌 요약/아이디어)
            styles: 생성할 스타일 목록 (None이면 기본 3가지)
            count: 생성할 버전 수 (최대 7개)

        Returns:
            RewriteVersion 리스트

        Example:
            >>> rewriter = AIRewriter()
            >>> versions = rewriter.generate_multiple_versions(
            ...     original_concept="고양이가 키보드 위에서 자다가 이메일을 보냄",
            ...     styles=['sarcastic', 'wholesome', 'dark'],
            ...     count=3
            ... )
            >>> for v in versions:
            ...     print(f"{v.style}: {v.content[:50]}... (유사도: {v.similarity:.1%})")
        """
        # 기본 스타일 선택
        if styles is None:
            default_styles = ['sarcastic', 'wholesome', 'dark']
            styles = default_styles[:count]
        else:
            # HumorStyle enum 값 검증
            available_styles = [s.value for s in HumorStyle]
            styles = [s for s in styles if s in available_styles][:count]

        versions = []

        for style in styles:
            try:
                # 스타일별 콘텐츠 생성
                result: GenerationResult = self.content_generator.generate(
                    original_concept=original_concept,
                    humor_style=style,
                    temperature=0.8  # 다양성을 위해 높은 temperature
                )

                # 유사도 체크
                similarity_result: SimilarityResult = self.similarity_checker.check_similarity(
                    original_text=original_concept,
                    generated_text=result.content
                )

                # 버전 객체 생성
                version = RewriteVersion(
                    style=style,
                    content=result.content,
                    similarity=similarity_result.overall_similarity,
                    is_fair_use=similarity_result.is_fair_use,
                    metadata={
                        'prompt_tokens': result.metadata.get('prompt_tokens', 0),
                        'completion_tokens': result.metadata.get('completion_tokens', 0),
                        'generation_time': result.metadata.get('generation_time', 0),
                        'similarity_details': {
                            'structural': similarity_result.structural_similarity,
                            'lexical': similarity_result.lexical_similarity,
                            'semantic': similarity_result.semantic_similarity
                        }
                    }
                )

                versions.append(version)

            except Exception as e:
                # 실패한 스타일은 건너뛰고 계속 진행
                print(f"Failed to generate {style} version: {e}")
                continue

        return versions

    def improve_paragraph(
        self,
        paragraph: str,
        improvement_goal: str = "더 재미있게",
        style: Optional[str] = None
    ) -> Dict:
        """
        특정 문단 개선

        하나의 문단을 AI로 리라이트하여 개선합니다.

        Args:
            paragraph: 개선할 문단
            improvement_goal: 개선 목표 (예: "더 재미있게", "더 간결하게", "더 상세하게")
            style: 유머 스타일 (선택, None이면 기본 스타일)

        Returns:
            {
                'original': str,
                'improved': str,
                'goal': str,
                'style': str,
                'metadata': dict
            }

        Example:
            >>> rewriter = AIRewriter()
            >>> result = rewriter.improve_paragraph(
            ...     paragraph="고양이가 키보드 위에서 잤다.",
            ...     improvement_goal="더 재미있고 구체적으로"
            ... )
            >>> print(result['improved'])
        """
        # 프롬프트 구성
        system_prompt = f"""당신은 유머 콘텐츠 작가입니다.
주어진 문단을 다음 목표에 맞춰 개선하세요: {improvement_goal}

개선 규칙:
1. 원본의 핵심 아이디어는 유지
2. 문체와 톤은 개선 목표에 맞춤
3. 적절한 길이 유지 (너무 길어지지 않게)
4. 유머와 재치 추가
5. 한국어로 자연스럽게 작성

개선할 문단:
{paragraph}

개선된 문단만 출력하세요 (추가 설명 없이):"""

        try:
            # LLM 호출
            improved = self.llm.generate_with_system_prompt(
                system_prompt="",  # 이미 user_prompt에 포함
                user_prompt=system_prompt,
                max_new_tokens=300,
                temperature=0.7
            )

            # 결과 정리
            improved = improved.strip()

            return {
                'original': paragraph,
                'improved': improved,
                'goal': improvement_goal,
                'style': style or 'default',
                'metadata': {
                    'original_length': len(paragraph),
                    'improved_length': len(improved),
                    'length_change': len(improved) - len(paragraph)
                }
            }

        except Exception as e:
            raise Exception(f"Failed to improve paragraph: {str(e)}")

    def generate_title(
        self,
        content: str,
        style: str = 'catchy',
        count: int = 3
    ) -> List[str]:
        """
        콘텐츠 기반 제목 생성

        콘텐츠를 분석하여 매력적인 제목을 여러 개 생성합니다.

        Args:
            content: 콘텐츠 본문
            style: 제목 스타일 ('catchy', 'informative', 'clickbait', 'simple')
            count: 생성할 제목 개수 (1-5개)

        Returns:
            제목 리스트

        Example:
            >>> rewriter = AIRewriter()
            >>> titles = rewriter.generate_title(
            ...     content="우리 집 고양이가 키보드에서 자다가 실수로 상사에게 이메일을 보냈다...",
            ...     style='catchy',
            ...     count=3
            ... )
            >>> for i, title in enumerate(titles, 1):
            ...     print(f"{i}. {title}")
        """
        # 스타일별 지시사항
        style_instructions = {
            'catchy': '눈길을 끄는 매력적인 제목 (호기심 유발)',
            'informative': '내용을 명확히 전달하는 정보성 제목',
            'clickbait': '클릭을 유도하는 자극적인 제목 (과도하지 않게)',
            'simple': '간단명료한 제목',
            'humorous': '유머러스하고 재치있는 제목'
        }

        instruction = style_instructions.get(style, style_instructions['catchy'])

        # 콘텐츠 요약 (너무 길면 앞부분만)
        content_preview = content[:500] if len(content) > 500 else content

        # 프롬프트 구성
        prompt = f"""다음 콘텐츠에 어울리는 제목을 {count}개 생성하세요.

제목 스타일: {instruction}

제목 규칙:
1. 한글 기준 10-30자 이내
2. 핵심 내용을 담되 흥미롭게
3. 이모지 사용 가능 (선택)
4. 각 제목은 한 줄에 하나씩
5. 번호나 기호 없이 제목만 출력

콘텐츠:
{content_preview}

제목 {count}개:"""

        try:
            # LLM 호출
            response = self.llm.generate_with_system_prompt(
                system_prompt="당신은 제목 작성 전문가입니다.",
                user_prompt=prompt,
                max_new_tokens=200,
                temperature=0.9  # 다양성을 위해 높은 temperature
            )

            # 제목 파싱
            titles = []
            for line in response.strip().split('\n'):
                line = line.strip()
                # 번호 제거 (예: "1. ", "1) ", "- " 등)
                line = line.lstrip('0123456789.-) ')
                if line and len(line) >= 5:  # 최소 5자 이상
                    titles.append(line)

            # 요청한 개수만큼만 반환
            return titles[:count]

        except Exception as e:
            raise Exception(f"Failed to generate titles: {str(e)}")

    def check_fair_use(
        self,
        original_text: str,
        generated_text: str,
        threshold: float = 0.70
    ) -> Dict:
        """
        Fair Use 준수 확인

        원본과 생성된 텍스트의 유사도를 체크하여 Fair Use 준수 여부를 판정합니다.

        Args:
            original_text: 원본 텍스트
            generated_text: 생성된 텍스트
            threshold: Fair Use 임계값 (기본 70%)

        Returns:
            {
                'is_fair_use': bool,
                'overall_similarity': float,
                'structural_similarity': float,
                'lexical_similarity': float,
                'semantic_similarity': float,
                'recommendation': str,
                'details': dict
            }

        Example:
            >>> rewriter = AIRewriter()
            >>> result = rewriter.check_fair_use(
            ...     original_text="원본 텍스트",
            ...     generated_text="생성된 텍스트"
            ... )
            >>> if result['is_fair_use']:
            ...     print("✓ Fair Use 준수")
            ... else:
            ...     print("✗ 유사도가 너무 높습니다. 재생성이 필요합니다.")
        """
        # 유사도 체크
        similarity_result: SimilarityResult = self.similarity_checker.check_similarity(
            original_text=original_text,
            generated_text=generated_text,
            threshold=threshold
        )

        # 추천 메시지 생성
        if similarity_result.is_fair_use:
            recommendation = "✓ Fair Use 준수: 충분히 재창작되었습니다."
        else:
            recommendation = f"✗ 유사도 {similarity_result.overall_similarity:.1%} (임계값: {threshold:.1%}). 재생성을 권장합니다."

        # 상세 분석
        details = {
            'threshold': threshold,
            'passed': similarity_result.is_fair_use,
            'similarity_breakdown': {
                'structural': {
                    'score': similarity_result.structural_similarity,
                    'weight': 0.3,
                    'description': '문장 구조 유사도'
                },
                'lexical': {
                    'score': similarity_result.lexical_similarity,
                    'weight': 0.5,
                    'description': '어휘 유사도'
                },
                'semantic': {
                    'score': similarity_result.semantic_similarity,
                    'weight': 0.2,
                    'description': '의미 유사도'
                }
            }
        }

        return {
            'is_fair_use': similarity_result.is_fair_use,
            'overall_similarity': similarity_result.overall_similarity,
            'structural_similarity': similarity_result.structural_similarity,
            'lexical_similarity': similarity_result.lexical_similarity,
            'semantic_similarity': similarity_result.semantic_similarity,
            'recommendation': recommendation,
            'details': details
        }

    def rewrite_with_feedback(
        self,
        original_concept: str,
        current_draft: str,
        feedback: str,
        style: Optional[str] = None
    ) -> Dict:
        """
        피드백 기반 재작성

        현재 초안에 대한 피드백을 반영하여 재작성합니다.

        Args:
            original_concept: 원본 컨셉
            current_draft: 현재 초안
            feedback: 개선 피드백 (예: "더 짧게", "농담을 더 추가", "진지하게")
            style: 유머 스타일 (선택)

        Returns:
            {
                'original_draft': str,
                'revised_draft': str,
                'feedback_applied': str,
                'similarity_to_original': float,
                'metadata': dict
            }

        Example:
            >>> rewriter = AIRewriter()
            >>> result = rewriter.rewrite_with_feedback(
            ...     original_concept="고양이가 이메일을 실수로 보냄",
            ...     current_draft="우리 집 고양이가 키보드를 밟아서...",
            ...     feedback="더 짧고 임팩트 있게 수정해주세요"
            ... )
            >>> print(result['revised_draft'])
        """
        # 프롬프트 구성
        prompt = f"""당신은 유머 콘텐츠 편집자입니다.

원본 컨셉:
{original_concept}

현재 초안:
{current_draft}

개선 피드백:
{feedback}

위 피드백을 반영하여 초안을 개선하세요.

개선 규칙:
1. 피드백의 핵심 요청사항을 최우선으로 반영
2. 원본 컨셉의 핵심은 유지
3. 자연스러운 한국어로 작성
4. 유머와 재치 유지

개선된 초안만 출력하세요 (추가 설명 없이):"""

        try:
            # LLM 호출
            revised_draft = self.llm.generate_with_system_prompt(
                system_prompt="",
                user_prompt=prompt,
                max_new_tokens=400,
                temperature=0.7
            )

            revised_draft = revised_draft.strip()

            # 원본 컨셉과의 유사도 체크
            similarity_result = self.similarity_checker.check_similarity(
                original_text=original_concept,
                generated_text=revised_draft
            )

            return {
                'original_draft': current_draft,
                'revised_draft': revised_draft,
                'feedback_applied': feedback,
                'similarity_to_original': similarity_result.overall_similarity,
                'is_fair_use': similarity_result.is_fair_use,
                'metadata': {
                    'original_length': len(current_draft),
                    'revised_length': len(revised_draft),
                    'length_change': len(revised_draft) - len(current_draft),
                    'style': style or 'default'
                }
            }

        except Exception as e:
            raise Exception(f"Failed to rewrite with feedback: {str(e)}")


# 글로벌 인스턴스 (싱글톤)
_ai_rewriter_instance = None


def get_ai_rewriter() -> AIRewriter:
    """
    AIRewriter 싱글톤 인스턴스 반환

    Returns:
        AIRewriter 인스턴스
    """
    global _ai_rewriter_instance
    if _ai_rewriter_instance is None:
        _ai_rewriter_instance = AIRewriter()
    return _ai_rewriter_instance
