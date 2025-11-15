"""
Fair Use 유사도 체크 서비스

원본 콘텐츠와 생성된 콘텐츠의 유사도를 측정하여
Fair Use 준수 여부를 판단합니다.
"""
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    """유사도 체크 결과"""
    overall_similarity: float  # 전체 유사도 (0.0-1.0)
    structural_similarity: float  # 구조적 유사도
    lexical_similarity: float  # 어휘적 유사도
    semantic_similarity: float  # 의미적 유사도 (향후 구현)
    is_fair_use_compliant: bool  # Fair Use 준수 여부 (< 0.7)
    details: Dict[str, any]


class SimilarityChecker:
    """
    유사도 체크 서비스

    다양한 방법으로 원본과 생성된 콘텐츠의 유사도를 측정합니다.
    Fair Use 가이드라인: 70% 미만 유사도 권장
    """

    FAIR_USE_THRESHOLD = 0.7  # 70% 미만이면 Fair Use 준수

    def check_similarity(
        self,
        original_text: str,
        generated_text: str
    ) -> SimilarityResult:
        """
        전체 유사도 체크

        Args:
            original_text: 원본 텍스트
            generated_text: 생성된 텍스트

        Returns:
            SimilarityResult 객체
        """
        # 1. 구조적 유사도 (문장 구조, 길이 등)
        structural_sim = self._check_structural_similarity(
            original_text,
            generated_text
        )

        # 2. 어휘적 유사도 (단어 겹침)
        lexical_sim = self._check_lexical_similarity(
            original_text,
            generated_text
        )

        # 3. 의미적 유사도 (향후 임베딩 모델 활용)
        semantic_sim = 0.0  # TODO: Phase 7에서 구현

        # 전체 유사도 (가중 평균)
        overall_sim = (
            structural_sim * 0.3 +
            lexical_sim * 0.5 +
            semantic_sim * 0.2
        )

        is_compliant = overall_sim < self.FAIR_USE_THRESHOLD

        return SimilarityResult(
            overall_similarity=overall_sim,
            structural_similarity=structural_sim,
            lexical_similarity=lexical_sim,
            semantic_similarity=semantic_sim,
            is_fair_use_compliant=is_compliant,
            details={
                'threshold': self.FAIR_USE_THRESHOLD,
                'weights': {
                    'structural': 0.3,
                    'lexical': 0.5,
                    'semantic': 0.2
                }
            }
        )

    def _check_structural_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        구조적 유사도 측정

        문장 개수, 문장 길이, 단락 구조 등을 비교합니다.

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트

        Returns:
            유사도 (0.0-1.0)
        """
        # 문장 분리
        sentences1 = self._split_sentences(text1)
        sentences2 = self._split_sentences(text2)

        # 문장 개수 유사도
        sent_count_sim = 1.0 - abs(len(sentences1) - len(sentences2)) / max(
            len(sentences1), len(sentences2), 1
        )

        # 평균 문장 길이 유사도
        avg_len1 = sum(len(s) for s in sentences1) / max(len(sentences1), 1)
        avg_len2 = sum(len(s) for s in sentences2) / max(len(sentences2), 1)
        len_diff = abs(avg_len1 - avg_len2) / max(avg_len1, avg_len2, 1)
        avg_len_sim = 1.0 - len_diff

        # 전체 길이 유사도
        total_len_sim = 1.0 - abs(len(text1) - len(text2)) / max(
            len(text1), len(text2), 1
        )

        # 가중 평균
        structural_sim = (
            sent_count_sim * 0.4 +
            avg_len_sim * 0.3 +
            total_len_sim * 0.3
        )

        return min(structural_sim, 1.0)

    def _check_lexical_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        어휘적 유사도 측정 (Jaccard 유사도)

        단어 집합의 겹침을 측정합니다.

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트

        Returns:
            유사도 (0.0-1.0)
        """
        # 단어 추출 (명사, 동사 등 의미 있는 단어)
        words1 = self._extract_meaningful_words(text1)
        words2 = self._extract_meaningful_words(text2)

        if not words1 and not words2:
            return 0.0

        # Jaccard 유사도
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        jaccard = intersection / union

        # N-gram 유사도 (2-gram, 3-gram)
        bigram_sim = self._ngram_similarity(text1, text2, n=2)
        trigram_sim = self._ngram_similarity(text1, text2, n=3)

        # 가중 평균
        lexical_sim = (
            jaccard * 0.5 +
            bigram_sim * 0.3 +
            trigram_sim * 0.2
        )

        return min(lexical_sim, 1.0)

    def _split_sentences(self, text: str) -> List[str]:
        """
        텍스트를 문장으로 분리

        Args:
            text: 입력 텍스트

        Returns:
            문장 리스트
        """
        # 한국어 문장 분리 (., !, ?, 줄바꿈 기준)
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _extract_meaningful_words(self, text: str) -> set:
        """
        의미 있는 단어 추출

        Args:
            text: 입력 텍스트

        Returns:
            단어 집합
        """
        # 한글, 영문, 숫자만 추출
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        # 단어 분리
        words = text.lower().split()

        # 불용어 제거 (조사, 접속사 등)
        stopwords = {
            '은', '는', '이', '가', '을', '를', '의', '에', '에서', '으로',
            '와', '과', '도', '만', '까지', '부터', '보다', '처럼', '같이',
            '그', '저', '이', '그런', '저런', '이런', '것', '수',
            '등', '및', '또', '또한', '그리고', '하지만', '그러나',
            '있다', '없다', '이다', '아니다', '하다', '되다', '않다'
        }

        meaningful_words = {
            w for w in words
            if len(w) >= 2 and w not in stopwords
        }

        return meaningful_words

    def _ngram_similarity(
        self,
        text1: str,
        text2: str,
        n: int = 2
    ) -> float:
        """
        N-gram 유사도 측정

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            n: N-gram 크기

        Returns:
            유사도 (0.0-1.0)
        """
        # N-gram 생성
        ngrams1 = self._get_ngrams(text1, n)
        ngrams2 = self._get_ngrams(text2, n)

        if not ngrams1 and not ngrams2:
            return 0.0

        # Jaccard 유사도
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        if union == 0:
            return 0.0

        return intersection / union

    def _get_ngrams(self, text: str, n: int) -> set:
        """
        N-gram 집합 생성

        Args:
            text: 입력 텍스트
            n: N-gram 크기

        Returns:
            N-gram 집합
        """
        # 공백 제거
        text = ''.join(text.split())

        if len(text) < n:
            return set()

        ngrams = {
            text[i:i+n]
            for i in range(len(text) - n + 1)
        }

        return ngrams

    def check_draft_similarity(
        self,
        original_concept: str,
        draft_content: str
    ) -> SimilarityResult:
        """
        Draft의 Fair Use 준수 여부 체크

        Args:
            original_concept: 원본 컨셉
            draft_content: Draft 내용

        Returns:
            SimilarityResult 객체
        """
        return self.check_similarity(original_concept, draft_content)

    def batch_check(
        self,
        original_texts: List[str],
        generated_texts: List[str]
    ) -> List[SimilarityResult]:
        """
        여러 텍스트 배치 체크

        Args:
            original_texts: 원본 텍스트 리스트
            generated_texts: 생성된 텍스트 리스트

        Returns:
            SimilarityResult 리스트
        """
        if len(original_texts) != len(generated_texts):
            raise ValueError("Original and generated lists must have same length")

        results = []
        for orig, gen in zip(original_texts, generated_texts):
            result = self.check_similarity(orig, gen)
            results.append(result)

        return results

    def get_fair_use_report(
        self,
        similarity_result: SimilarityResult
    ) -> str:
        """
        Fair Use 준수 리포트 생성

        Args:
            similarity_result: SimilarityResult 객체

        Returns:
            리포트 문자열
        """
        status = "✅ Fair Use 준수" if similarity_result.is_fair_use_compliant else "⚠️ Fair Use 위반 가능성"

        report = f"""
=== Fair Use 유사도 체크 리포트 ===

**전체 유사도**: {similarity_result.overall_similarity:.2%}
**판정**: {status}

**세부 분석**:
- 구조적 유사도: {similarity_result.structural_similarity:.2%}
- 어휘적 유사도: {similarity_result.lexical_similarity:.2%}
- 의미적 유사도: {similarity_result.semantic_similarity:.2%} (향후 구현)

**기준 임계값**: {self.FAIR_USE_THRESHOLD:.0%}

**권장 사항**:
"""

        if similarity_result.is_fair_use_compliant:
            report += "- 현재 콘텐츠는 Fair Use 기준을 충족합니다.\n"
            report += "- 그대로 사용하셔도 됩니다.\n"
        else:
            report += "- ⚠️ 유사도가 높아 Fair Use 위반 가능성이 있습니다.\n"
            report += "- 추가 수정을 권장합니다:\n"
            report += "  1. 문장 구조를 더 다르게 변경\n"
            report += "  2. 다른 어휘 사용\n"
            report += "  3. 배경이나 등장인물 변경\n"

        return report.strip()


# 테스트용 함수
def test_similarity_checker():
    """SimilarityChecker 테스트"""
    checker = SimilarityChecker()

    # 테스트 케이스 1: 거의 동일한 텍스트
    original1 = "회의 중에 카메라가 꺼져있는 줄 알고 하품을 했는데 사실 켜져있었다"
    generated1 = "미팅 중에 카메라가 off인 줄 알고 하품했는데 실제로는 on이었다"

    result1 = checker.check_similarity(original1, generated1)
    print("=== Test Case 1: High Similarity ===")
    print(f"Original: {original1}")
    print(f"Generated: {generated1}")
    print(f"Overall: {result1.overall_similarity:.2%}")
    print(f"Fair Use: {result1.is_fair_use_compliant}")
    print()

    # 테스트 케이스 2: 완전히 다른 텍스트
    original2 = "회의 중에 카메라가 꺼져있는 줄 알고 하품을 했는데 사실 켜져있었다"
    generated2 = """오늘 팀장님이 갑자기 회의실로 오셨다.

"김대리, 이번 프로젝트 진행 상황 어때요?"

나: "네... 순조롭게 진행 중입니다..."

사실 진도는 20%도 안 나갔다.

팀장님: "좋아요. 내일 중간 보고 준비해주세요."

...내일?

집에 못 가는구나."""

    result2 = checker.check_similarity(original2, generated2)
    print("=== Test Case 2: Low Similarity ===")
    print(f"Original: {original2}")
    print(f"Generated: {generated2[:50]}...")
    print(f"Overall: {result2.overall_similarity:.2%}")
    print(f"Fair Use: {result2.is_fair_use_compliant}")
    print()

    # 리포트 출력
    print("=== Fair Use Report (Test Case 1) ===")
    print(checker.get_fair_use_report(result1))
    print()

    print("=== Fair Use Report (Test Case 2) ===")
    print(checker.get_fair_use_report(result2))


if __name__ == "__main__":
    test_similarity_checker()
