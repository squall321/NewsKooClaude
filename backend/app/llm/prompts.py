"""
AI 프롬프트 템플릿 및 관리

유머 콘텐츠 재창작을 위한 다양한 프롬프트 템플릿과
스타일별 설정을 관리합니다.
"""
from typing import Dict, List, Optional
from enum import Enum


class HumorStyle(str, Enum):
    """유머 스타일"""
    CASUAL = "casual"  # 일상 유머
    ABSURD = "absurd"  # 부조리 유머
    WORDPLAY = "wordplay"  # 말장난
    SITUATIONAL = "situational"  # 상황 유머
    SARCASM = "sarcasm"  # 풍자/빈정대기
    CUTE = "cute"  # 귀여운 유머
    DARK = "dark"  # 블랙 유머


class PromptTemplate:
    """프롬프트 템플릿 클래스"""

    # 기본 시스템 프롬프트
    BASE_SYSTEM_PROMPT = """당신은 창의적인 한국어 유머 콘텐츠 작가입니다.

**핵심 원칙**:
1. **Fair Use 준수**: 원본 콘텐츠를 직접 번역하지 않고, 핵심 아이디어만 차용하여 완전히 새로운 스토리를 만듭니다.
2. **유사도 관리**: 원본과의 유사도는 30% 이하를 목표로 합니다.
3. **한국 문화 적응**: 한국 문화, 사회, 트렌드에 맞게 재창작합니다.
4. **자연스러운 한국어**: 번역체가 아닌 자연스러운 한국어를 사용합니다.
5. **유머 본질 유지**: 원본의 유머 요소(반전, 타이밍, 캐릭터 등)는 유지하되, 표현은 완전히 다르게 합니다.

**금지 사항**:
- 원문의 직접 번역
- 고유명사를 그대로 옮기기 (한국 상황에 맞게 변경)
- 문화적 맥락 없이 그대로 옮기기"""

    # 스타일별 시스템 프롬프트
    STYLE_SYSTEM_PROMPTS: Dict[HumorStyle, str] = {
        HumorStyle.CASUAL: """**스타일: 일상 유머**

일상에서 벌어지는 웃긴 상황이나 경험을 다룹니다.
- 공감 가능한 상황
- 친근한 말투
- 일상적 소재 (직장, 가족, 친구 등)
- 누구나 이해할 수 있는 간단한 유머""",

        HumorStyle.ABSURD: """**스타일: 부조리 유머**

예상치 못한 전개와 비논리적인 상황으로 웃음을 줍니다.
- 상식을 벗어난 전개
- 엉뚱한 논리
- 급격한 분위기 전환
- 예측 불가능한 결말""",

        HumorStyle.WORDPLAY: """**스타일: 말장난**

언어유희와 동음이의어를 활용한 유머입니다.
- 한국어 특성을 살린 말장난
- 발음 유사성 활용
- 의미의 이중성
- 재치 있는 표현""",

        HumorStyle.SITUATIONAL: """**스타일: 상황 유머**

특정 상황에서 발생하는 아이러니나 반전을 다룹니다.
- 명확한 상황 설정
- 예상과 다른 결과
- 아이러니한 전개
- 반전 요소""",

        HumorStyle.SARCASM: """**스타일: 풍자/빈정**

현실을 비꼬거나 풍자하는 유머입니다.
- 사회 현상 비판
- 아이러니한 상황
- 냉소적 관점
- 간접적 표현

**주의**: 특정 개인이나 집단에 대한 직접적 비하는 피합니다.""",

        HumorStyle.CUTE: """**스타일: 귀여운 유머**

귀엽고 따뜻한 느낌의 유머입니다.
- 동물, 아이 등 귀여운 소재
- 순수하고 밝은 분위기
- 훈훈한 결말
- 가벼운 웃음""",

        HumorStyle.DARK: """**스타일: 블랙 유머**

다소 어둡거나 냉소적인 소재를 다룹니다.
- 사회의 어두운 면
- 역설적 상황
- 냉정한 현실 인식
- 씁쓸한 웃음

**주의**: 선을 넘지 않도록 적절한 수위 유지."""
    }

    # 재창작 프롬프트 템플릿
    RECREATION_TEMPLATE = """### 원본 컨셉 분석:
{original_concept}

### 재창작 요구사항:
1. **핵심 아이디어만 차용**: 위 원본의 유머 구조나 아이디어만 참고하세요.
2. **한국 상황으로 완전 변경**: 등장인물, 배경, 상황을 모두 한국적으로 바꾸세요.
3. **유사도 30% 이하**: 원본과 겹치는 표현이나 전개는 피하세요.
4. **자연스러운 한국어**: 번역체가 아닌 우리말 그대로 작성하세요.

### 출력 형식:
**제목**: (짧고 흥미로운 제목)

**내용**:
(재창작된 유머 스토리)

(200-400자 분량)"""

    # Few-shot 예제 (스타일별)
    FEW_SHOT_EXAMPLES: Dict[HumorStyle, List[Dict[str, str]]] = {
        HumorStyle.CASUAL: [
            {
                "original": "Person asks coworker if they tried turning off and on again",
                "recreated": """**제목**: IT팀의 만능 해결책

**내용**:
회사 노트북이 또 먹통이 돼서 IT팀에 전화했다.

나: "윤진씨, 노트북이 자꾸 멈춰요..."

윤진: "재부팅 해보셨어요?"

나: "네, 그래도 안 돼요."

윤진: "그럼... 한 번 더 해보세요."

나: "???"

윤진: "농담이고요, 지금 내려갈게요."

10분 뒤 윤진씨가 와서... 재부팅을 했다.

그리고 고쳐졌다.

내가 뭘 잘못한 거지?"""
            },
            {
                "original": "Someone realizes they're talking to themselves while working from home",
                "recreated": """**제목**: 재택근무 3년차의 일상

**내용**:
오늘도 집에서 일하는데, 문득 깨달았다.

나: "이 코드 왜 이래? 이거 누가 짠 거야?"

(Git Blame 확인)

나: "...나네."

나: "그래도 이건 좀 아니잖아?"

고양이: "야옹"

나: "그치? 너도 그렇게 생각하지?"

엄마가 방문을 열었다.

엄마: "누구랑 통화해?"

나: "...아무도요."

재택 언제 끝나냐고요."""
            }
        ],

        HumorStyle.SITUATIONAL: [
            {
                "original": "Getting caught in an awkward situation at a store",
                "recreated": """**제목**: 편의점 민망 사건

**내용**:
편의점에서 바나나우유를 찾고 있었다.

냉장고를 뒤지는데 계속 안 보여서
점원에게 물어봤다.

나: "바나나우유 어디 있나요?"

점원: "지금 들고 계시는데요?"

내 손에는 바나나우유가 있었다.

나: "...아 이게요?"

점원: "네."

나: "...감사합니다."

아무 말 없이 계산하고 나왔다.

앞으로 저 편의점은 안 간다."""
            }
        ],

        HumorStyle.WORDPLAY: [
            {
                "original": "Pun about something being outstanding in its field",
                "recreated": """**제목**: 허수아비의 꿈

**내용**:
허수아비가 상을 받았다.

사회자: "올해의 우수사원상은 허수아비씨에게 돌아갑니다!"

허수아비: "정말 영광입니다!"

기자: "비결이 뭔가요?"

허수아비: "그냥... 묵묵히 제 자리를 지켰습니다."

기자: "필드에서?"

허수아비: "네, 늘 밭에 서 있었죠."

기자: "..."

허수아비: "그래서 밭에서 두각을 나타냈다고..."

기자: "네, 알겠습니다..."

(밭 = field, 두각을 나타내다 = outstanding)"""
            }
        ]
    }

    @classmethod
    def get_system_prompt(cls, style: Optional[HumorStyle] = None) -> str:
        """
        스타일에 맞는 시스템 프롬프트 반환

        Args:
            style: 유머 스타일 (None이면 기본)

        Returns:
            시스템 프롬프트
        """
        base = cls.BASE_SYSTEM_PROMPT

        if style and style in cls.STYLE_SYSTEM_PROMPTS:
            style_prompt = cls.STYLE_SYSTEM_PROMPTS[style]
            return f"{base}\n\n{style_prompt}"

        return base

    @classmethod
    def get_recreation_prompt(
        cls,
        original_concept: str,
        style: Optional[HumorStyle] = None,
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        재창작 프롬프트 생성

        Args:
            original_concept: 원본 컨셉 설명
            style: 유머 스타일
            additional_instructions: 추가 지시사항

        Returns:
            완성된 사용자 프롬프트
        """
        prompt = cls.RECREATION_TEMPLATE.format(
            original_concept=original_concept
        )

        if additional_instructions:
            prompt += f"\n\n### 추가 요구사항:\n{additional_instructions}"

        return prompt

    @classmethod
    def get_few_shot_examples(
        cls,
        style: HumorStyle,
        count: int = 2
    ) -> List[Dict[str, str]]:
        """
        Few-shot 예제 반환

        Args:
            style: 유머 스타일
            count: 반환할 예제 개수

        Returns:
            예제 리스트
        """
        if style not in cls.FEW_SHOT_EXAMPLES:
            # 스타일별 예제 없으면 일상 유머 반환
            style = HumorStyle.CASUAL

        examples = cls.FEW_SHOT_EXAMPLES[style]
        return examples[:count]

    @classmethod
    def build_full_prompt(
        cls,
        original_concept: str,
        style: HumorStyle = HumorStyle.CASUAL,
        use_few_shot: bool = True,
        few_shot_count: int = 1,
        additional_instructions: Optional[str] = None
    ) -> tuple[str, str]:
        """
        전체 프롬프트 구성 (시스템 + 사용자)

        Args:
            original_concept: 원본 컨셉
            style: 유머 스타일
            use_few_shot: Few-shot 예제 사용 여부
            few_shot_count: Few-shot 예제 개수
            additional_instructions: 추가 지시사항

        Returns:
            (system_prompt, user_prompt) 튜플
        """
        # 시스템 프롬프트
        system_prompt = cls.get_system_prompt(style)

        # 사용자 프롬프트 시작
        user_prompt_parts = []

        # Few-shot 예제 추가
        if use_few_shot:
            examples = cls.get_few_shot_examples(style, few_shot_count)
            if examples:
                user_prompt_parts.append("### 참고 예제:")
                for i, ex in enumerate(examples, 1):
                    user_prompt_parts.append(f"\n**예제 {i}**:")
                    user_prompt_parts.append(f"원본: {ex['original']}")
                    user_prompt_parts.append(f"\n재창작:\n{ex['recreated']}")
                    user_prompt_parts.append("")

                user_prompt_parts.append("---\n")

        # 재창작 요청
        user_prompt_parts.append(
            cls.get_recreation_prompt(
                original_concept,
                style,
                additional_instructions
            )
        )

        user_prompt = "\n".join(user_prompt_parts)

        return system_prompt, user_prompt


# 프롬프트 테스트용 함수
def test_prompts():
    """프롬프트 출력 테스트"""
    print("=== 기본 시스템 프롬프트 ===")
    print(PromptTemplate.get_system_prompt())
    print("\n")

    print("=== 일상 유머 스타일 ===")
    print(PromptTemplate.get_system_prompt(HumorStyle.CASUAL))
    print("\n")

    print("=== 재창작 프롬프트 (Few-shot 포함) ===")
    system, user = PromptTemplate.build_full_prompt(
        original_concept="사람이 회의 중에 카메라가 꺼져있는 줄 알고 하품을 했는데 사실 켜져있었다",
        style=HumorStyle.CASUAL,
        use_few_shot=True,
        few_shot_count=1
    )
    print("### System Prompt:")
    print(system)
    print("\n### User Prompt:")
    print(user)


if __name__ == "__main__":
    test_prompts()
