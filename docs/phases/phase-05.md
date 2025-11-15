# Phase 05: 로컬 LLM 환경 구축 ⭐

**난이도**: ⭐⭐⭐⭐⭐
**예상 소요 시간**: 4-6시간
**우선순위**: P0

## 목표

RTX 5070 TI로 EEVE-Korean-10.8B를 실행하여 API 비용 제로를 달성합니다.

## 선행 요구사항

- Phase 4 완료
- 관련 기술 스택 기본 이해

---

## 주요 구현 내용

### 핵심 작업

1. **CUDA 12.1 설치**
2. **PyTorch CUDA 설정**
3. **EEVE 모델 다운로드**
4. **INT8 양자화**
5. **LLMModelLoader 구현**
6. **추론 테스트**

---

## 생성/수정할 파일

- `app/llm/model_loader.py`
- `scripts/download_model.py`
- `scripts/quantize_model.py`

---

## 구현 단계

### 1단계: 환경 준비

이 Phase를 시작하기 전에 필요한 도구와 라이브러리를 설치합니다.

**확인 사항**:
- 이전 Phase 완료 확인
- 필요한 패키지 설치
- 개발 서버 실행 상태 확인

### 2단계: 핵심 구현

**1. CUDA 12.1 설치**
**2. PyTorch CUDA 설정**
**3. EEVE 모델 다운로드**
**4. INT8 양자화**
**5. LLMModelLoader 구현**
**6. 추론 테스트**

각 작업은 순차적으로 진행하며, 테스트를 거쳐 검증합니다.

### 3단계: 테스트

```python
# 테스트 코드 작성 예시
# pytest tests/test_phase_05.py -v
```

**테스트 항목**:
- 단위 테스트 (Unit Test)
- 통합 테스트 (Integration Test)
- 수동 테스트 (Manual Test)

### 4단계: 통합 및 검증

- 전체 시스템과 통합
- 기존 기능에 영향 없는지 확인
- 성능 테스트

---

## 완료 체크리스트

### 구현
- [ ] CUDA 12.1 설치
- [ ] PyTorch CUDA 설정
- [ ] EEVE 모델 다운로드
- [ ] INT8 양자화
- [ ] LLMModelLoader 구현
- [ ] 추론 테스트

### 품질 보증
- [ ] 코드 리뷰 (자체)
- [ ] 테스트 작성 및 통과
- [ ] 에러 핸들링 확인
- [ ] 로깅 적절히 추가

### 문서화
- [ ] 코드 주석 작성
- [ ] PROGRESS.md 업데이트
- [ ] Git 커밋 메시지 작성

---

## 코드 예제

### 핵심 구현

```python
# TODO: Phase 5 구현 시 실제 코드 추가
# 이 섹션은 구현 가이드로 활용됩니다

# 예시 코드 구조는 다음과 같습니다:
# 1. Import 문
# 2. 설정
# 3. 핵심 로직
# 4. Export
```

---

## 테스트

### 단위 테스트

```python
# tests/test_phase_05.py
import pytest

def test_phase_5_functionality():
    '''Phase 5 기능 테스트'''
    # TODO: 테스트 구현
    pass
```

### 실행

```bash
pytest tests/test_phase_05.py -v
```

---

## 문제 해결

### 자주 발생하는 문제

**문제 1**: [일반적인 문제]
- **증상**: [현상 설명]
- **원인**: [원인 분석]
- **해결**: [해결 방법]

**문제 2**: [성능 관련]
- **증상**: [느린 속도 등]
- **원인**: [병목 지점]
- **해결**: [최적화 방법]

---

## 다음 단계

Phase 5 완료 후:

1. **코드 커밋**
   ```bash
   git add .
   git commit -m "Phase 5: 로컬 LLM 환경 구축 ⭐"
   git push origin your-branch
   ```

2. **PROGRESS.md 업데이트**
   - 완료 날짜 기록
   - 주요 구현 내용 요약
   - 배운 점 기록

3. **Phase 6로 이동**

---

## 참고 자료

- [전체 로드맵](../DEVELOPMENT_ROADMAP.md#phase-5)
- [Phase Index](../PHASE_INDEX.md)
- [관련 기술 문서]

---

**완료 기준**:
✅ 모든 체크리스트 항목 완료
✅ 테스트 통과 (100%)
✅ 실제 작동 확인
✅ 문서화 완료
