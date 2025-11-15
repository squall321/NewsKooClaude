"""
AI 콘텐츠 생성 서비스

LLM을 활용한 유머 콘텐츠 재창작 및 품질 관리
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from app.llm.model_loader import get_llm_instance
from app.llm.prompts import PromptTemplate, HumorStyle
from app.models import Inspiration, WritingStyle, Draft
from app import db

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """콘텐츠 생성 결과"""
    title: str
    content: str
    style: str
    generation_time_sec: float
    token_count: int
    success: bool
    error_message: Optional[str] = None
    similarity_score: Optional[float] = None


class ContentGenerator:
    """
    AI 콘텐츠 생성 서비스

    EEVE-Korean-10.8B를 사용하여 원본 아이디어를 바탕으로
    Fair Use를 준수하는 한국어 유머 콘텐츠를 생성합니다.
    """

    def __init__(self, auto_load_model: bool = False):
        """
        Args:
            auto_load_model: True면 초기화 시 모델 로드
        """
        self.llm = get_llm_instance(auto_load=auto_load_model)

    def generate_from_inspiration(
        self,
        inspiration_id: int,
        style: HumorStyle = HumorStyle.CASUAL,
        use_few_shot: bool = True,
        max_retries: int = 2
    ) -> GenerationResult:
        """
        Inspiration 객체로부터 콘텐츠 생성

        Args:
            inspiration_id: Inspiration ID
            style: 유머 스타일
            use_few_shot: Few-shot 예제 사용 여부
            max_retries: 생성 실패 시 재시도 횟수

        Returns:
            GenerationResult 객체
        """
        # Inspiration 가져오기
        inspiration = Inspiration.query.get(inspiration_id)
        if not inspiration:
            return GenerationResult(
                title="",
                content="",
                style=style.value,
                generation_time_sec=0.0,
                token_count=0,
                success=False,
                error_message=f"Inspiration {inspiration_id} not found"
            )

        # 원본 컨셉 준비
        original_concept = inspiration.original_concept

        # 추가 지시사항 (있으면)
        additional_instructions = inspiration.adaptation_notes

        return self.generate(
            original_concept=original_concept,
            style=style,
            use_few_shot=use_few_shot,
            additional_instructions=additional_instructions,
            max_retries=max_retries
        )

    def generate(
        self,
        original_concept: str,
        style: HumorStyle = HumorStyle.CASUAL,
        use_few_shot: bool = True,
        additional_instructions: Optional[str] = None,
        max_retries: int = 2,
        **generation_kwargs
    ) -> GenerationResult:
        """
        원본 컨셉으로부터 콘텐츠 생성

        Args:
            original_concept: 원본 아이디어/컨셉
            style: 유머 스타일
            use_few_shot: Few-shot 예제 사용 여부
            additional_instructions: 추가 지시사항
            max_retries: 실패 시 재시도 횟수
            **generation_kwargs: LLM generate() 파라미터

        Returns:
            GenerationResult 객체
        """
        if not self.llm.is_loaded():
            return GenerationResult(
                title="",
                content="",
                style=style.value,
                generation_time_sec=0.0,
                token_count=0,
                success=False,
                error_message="LLM model not loaded. Call load_model() first."
            )

        # 프롬프트 구성
        system_prompt, user_prompt = PromptTemplate.build_full_prompt(
            original_concept=original_concept,
            style=style,
            use_few_shot=use_few_shot,
            few_shot_count=1 if use_few_shot else 0,
            additional_instructions=additional_instructions
        )

        # 생성 파라미터 기본값
        gen_params = {
            'max_new_tokens': 512,
            'temperature': 0.85,
            'top_p': 0.92,
            'top_k': 50,
            'repetition_penalty': 1.15
        }
        gen_params.update(generation_kwargs)

        # 생성 시도
        for attempt in range(max_retries + 1):
            try:
                start_time = datetime.now()

                # LLM 생성
                generated_text = self.llm.generate_with_system_prompt(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    **gen_params
                )

                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()

                # 결과 파싱
                title, content = self._parse_generated_text(generated_text)

                # 토큰 수 추정 (대략 한글 1글자 = 2 토큰)
                token_count = len(generated_text) * 2

                return GenerationResult(
                    title=title,
                    content=content,
                    style=style.value,
                    generation_time_sec=generation_time,
                    token_count=token_count,
                    success=True
                )

            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    return GenerationResult(
                        title="",
                        content="",
                        style=style.value,
                        generation_time_sec=0.0,
                        token_count=0,
                        success=False,
                        error_message=str(e)
                    )

        # Should not reach here
        return GenerationResult(
            title="",
            content="",
            style=style.value,
            generation_time_sec=0.0,
            token_count=0,
            success=False,
            error_message="Max retries exceeded"
        )

    def _parse_generated_text(self, text: str) -> tuple[str, str]:
        """
        생성된 텍스트에서 제목과 내용 추출

        Args:
            text: LLM 생성 텍스트

        Returns:
            (title, content) 튜플
        """
        lines = text.strip().split('\n')

        title = ""
        content_lines = []
        in_content = False

        for line in lines:
            line = line.strip()

            # 제목 찾기
            if line.startswith("**제목**:") or line.startswith("제목:"):
                title = line.split(':', 1)[1].strip()
                if title.startswith('**'):
                    title = title.strip('*').strip()
                continue

            # 내용 시작
            if line.startswith("**내용**:") or line.startswith("내용:"):
                in_content = True
                continue

            # 내용 수집
            if in_content and line:
                content_lines.append(line)

        content = '\n\n'.join(content_lines).strip()

        # 제목이 없으면 첫 줄을 제목으로
        if not title and content_lines:
            title = content_lines[0][:50]  # 첫 50자

        return title, content

    def create_draft_from_inspiration(
        self,
        inspiration_id: int,
        user_id: int,
        category_id: int,
        style: HumorStyle = HumorStyle.CASUAL,
        writing_style_id: Optional[int] = None,
        use_few_shot: bool = True
    ) -> Optional[Draft]:
        """
        Inspiration으로부터 Draft 생성

        Args:
            inspiration_id: Inspiration ID
            user_id: 작성자 ID
            category_id: 카테고리 ID
            style: 유머 스타일
            writing_style_id: WritingStyle ID (선택)
            use_few_shot: Few-shot 사용 여부

        Returns:
            생성된 Draft 객체 (실패 시 None)
        """
        # Inspiration 확인
        inspiration = Inspiration.query.get(inspiration_id)
        if not inspiration:
            logger.error(f"Inspiration {inspiration_id} not found")
            return None

        # 콘텐츠 생성
        result = self.generate_from_inspiration(
            inspiration_id=inspiration_id,
            style=style,
            use_few_shot=use_few_shot
        )

        if not result.success:
            logger.error(f"Content generation failed: {result.error_message}")
            return None

        # Draft 생성
        try:
            draft = Draft.create(
                user_id=user_id,
                category_id=category_id,
                inspiration_id=inspiration_id,
                writing_style_id=writing_style_id,
                title=result.title,
                content=result.content,
                ai_generated=True,
                generation_metadata={
                    'style': result.style,
                    'generation_time_sec': result.generation_time_sec,
                    'token_count': result.token_count,
                    'model': self.llm.model_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )

            db.session.commit()

            logger.info(f"Draft {draft.id} created from Inspiration {inspiration_id}")
            return draft

        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            db.session.rollback()
            return None

    def batch_generate(
        self,
        inspiration_ids: List[int],
        style: HumorStyle = HumorStyle.CASUAL,
        use_few_shot: bool = True
    ) -> List[GenerationResult]:
        """
        여러 Inspiration에 대해 배치 생성

        Args:
            inspiration_ids: Inspiration ID 리스트
            style: 유머 스타일
            use_few_shot: Few-shot 사용 여부

        Returns:
            GenerationResult 리스트
        """
        results = []

        for insp_id in inspiration_ids:
            result = self.generate_from_inspiration(
                inspiration_id=insp_id,
                style=style,
                use_few_shot=use_few_shot
            )
            results.append(result)

        return results

    def regenerate_draft(
        self,
        draft_id: int,
        style: Optional[HumorStyle] = None,
        use_few_shot: bool = True
    ) -> bool:
        """
        기존 Draft 재생성

        Args:
            draft_id: Draft ID
            style: 유머 스타일 (None이면 기존 스타일 유지)
            use_few_shot: Few-shot 사용 여부

        Returns:
            성공 여부
        """
        draft = Draft.query.get(draft_id)
        if not draft:
            logger.error(f"Draft {draft_id} not found")
            return False

        if not draft.inspiration_id:
            logger.error(f"Draft {draft_id} has no associated inspiration")
            return False

        # 스타일 결정
        if style is None:
            metadata = draft.generation_metadata or {}
            style_str = metadata.get('style', HumorStyle.CASUAL.value)
            style = HumorStyle(style_str)

        # 재생성
        result = self.generate_from_inspiration(
            inspiration_id=draft.inspiration_id,
            style=style,
            use_few_shot=use_few_shot
        )

        if not result.success:
            logger.error(f"Regeneration failed: {result.error_message}")
            return False

        # Draft 업데이트
        try:
            draft.title = result.title
            draft.content = result.content
            draft.generation_metadata = {
                'style': result.style,
                'generation_time_sec': result.generation_time_sec,
                'token_count': result.token_count,
                'model': self.llm.model_name,
                'timestamp': datetime.utcnow().isoformat(),
                'regenerated': True
            }

            db.session.commit()
            logger.info(f"Draft {draft_id} regenerated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update draft: {e}")
            db.session.rollback()
            return False


# 테스트용 함수
def test_content_generator():
    """ContentGenerator 테스트"""
    from app import create_app

    app = create_app('testing')

    with app.app_context():
        generator = ContentGenerator(auto_load_model=False)

        # LLM 없이 프롬프트만 테스트
        print("=== Test: Generate Prompt ===")
        system, user = PromptTemplate.build_full_prompt(
            original_concept="회의 중 카메라 켜진 줄 모르고 하품",
            style=HumorStyle.CASUAL,
            use_few_shot=True
        )
        print("System:", system[:200], "...")
        print("User:", user[:200], "...")


if __name__ == "__main__":
    test_content_generator()
