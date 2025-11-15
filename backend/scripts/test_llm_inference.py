#!/usr/bin/env python3
"""
LLM 추론 테스트 스크립트

EEVE-Korean-10.8B 모델을 로드하고 간단한 추론을 수행하여
설정이 올바른지 확인합니다.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.llm.model_loader import LLMModelLoader
import torch

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_inference(llm: LLMModelLoader):
    """기본 추론 테스트"""
    logger.info("\n=== Test 1: Basic Inference ===")

    prompt = "한국의 수도는"
    logger.info(f"Prompt: {prompt}")

    result = llm.generate(
        prompt,
        max_new_tokens=50,
        temperature=0.7
    )

    logger.info(f"Generated: {result}")
    return result


def test_korean_humor_generation(llm: LLMModelLoader):
    """한국어 유머 생성 테스트"""
    logger.info("\n=== Test 2: Korean Humor Generation ===")

    system_prompt = "당신은 창의적인 한국어 유머 작가입니다. 주어진 소재를 바탕으로 재미있는 짧은 이야기를 만들어주세요."
    user_prompt = "주제: 고양이가 컴퓨터 키보드 위에 앉아있는 상황"

    logger.info(f"System: {system_prompt}")
    logger.info(f"User: {user_prompt}")

    result = llm.generate_with_system_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_new_tokens=256,
        temperature=0.8,
        top_p=0.9
    )

    logger.info(f"Generated:\n{result}")
    return result


def test_content_recreation(llm: LLMModelLoader):
    """콘텐츠 재창작 테스트"""
    logger.info("\n=== Test 3: Content Recreation ===")

    system_prompt = """당신은 해외 유머 콘텐츠를 한국 문화에 맞게 재창작하는 전문가입니다.
원본의 핵심 아이디어만 차용하고, 완전히 새로운 한국어 스토리를 만들어주세요.
유사도는 30% 이하를 목표로 합니다."""

    user_prompt = """원본 컨셉: "회사에서 프린터가 고장났는데, IT 담당자가 '껐다 켜보셨어요?'라고 물어봄"

한국 상황에 맞게 재창작해주세요:"""

    logger.info(f"System: {system_prompt}")
    logger.info(f"User: {user_prompt}")

    result = llm.generate_with_system_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_new_tokens=300,
        temperature=0.85,
        top_p=0.92,
        repetition_penalty=1.15
    )

    logger.info(f"Recreated Content:\n{result}")
    return result


def test_batch_generation(llm: LLMModelLoader):
    """배치 생성 테스트"""
    logger.info("\n=== Test 4: Batch Generation ===")

    prompts = [
        "오늘 날씨는",
        "Python 프로그래밍의 장점은",
        "서울의 유명한 관광지는"
    ]

    results = llm.batch_generate(
        prompts,
        max_new_tokens=30,
        temperature=0.7
    )

    for prompt, result in zip(prompts, results):
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Result: {result}\n")

    return results


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Test LLM inference with EEVE-Korean-10.8B"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yanolja/EEVE-Korean-10.8B-v1.0",
        help="HuggingFace model ID"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cuda", "cpu"],
        help="Device to run on (cuda or cpu)"
    )
    parser.add_argument(
        "--no-8bit",
        action="store_true",
        help="Disable 8-bit quantization (requires more VRAM)"
    )
    parser.add_argument(
        "--test",
        type=str,
        default="all",
        choices=["all", "basic", "humor", "recreation", "batch"],
        help="Which test to run"
    )

    args = parser.parse_args()

    # CUDA 사용 가능 여부 확인
    if args.device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA not available. Falling back to CPU.")
        args.device = "cpu"

    # 시스템 정보 출력
    logger.info("=== System Information ===")
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        logger.info(f"Total VRAM: {total_vram:.2f} GB")

    # LLM 로더 초기화
    logger.info("\n=== Initializing LLM ===")
    llm = LLMModelLoader(
        model_name=args.model,
        device=args.device,
        load_in_8bit=(not args.no_8bit) and args.device == "cuda",
        use_flash_attention=True
    )

    # 모델 로드
    try:
        llm.load_model()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.error("\nMake sure you've downloaded the model first:")
        logger.error("  python scripts/download_model.py")
        sys.exit(1)

    # 모델 정보 출력
    model_info = llm.get_model_info()
    logger.info("\n=== Model Information ===")
    for key, value in model_info.items():
        logger.info(f"{key}: {value}")

    # 테스트 실행
    try:
        if args.test in ["all", "basic"]:
            test_basic_inference(llm)

        if args.test in ["all", "humor"]:
            test_korean_humor_generation(llm)

        if args.test in ["all", "recreation"]:
            test_content_recreation(llm)

        if args.test in ["all", "batch"]:
            test_batch_generation(llm)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # 모델 언로드
        logger.info("\n=== Cleaning up ===")
        llm.unload_model()

    logger.info("\n=== All tests completed successfully! ===")


if __name__ == "__main__":
    main()
