#!/usr/bin/env python3
"""
EEVE-Korean-10.8B 모델 다운로드 스크립트

HuggingFace에서 모델을 다운로드하고 로컬 캐시에 저장합니다.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_model(
    model_name: str = "yanolja/EEVE-Korean-10.8B-v1.0",
    cache_dir: str = None,
    token: str = None
):
    """
    HuggingFace에서 모델을 다운로드합니다.

    Args:
        model_name: HuggingFace 모델 ID
        cache_dir: 다운로드 경로 (None이면 기본 경로: ~/.cache/huggingface)
        token: HuggingFace API 토큰 (private 모델용)
    """
    logger.info(f"Downloading model: {model_name}")
    logger.info(f"Cache directory: {cache_dir or 'default (~/.cache/huggingface)'}")

    # CUDA 사용 가능 여부 확인
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA available: {cuda_available}")

    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        logger.info(f"GPU: {device_name}")
        logger.info(f"Total VRAM: {vram_total:.2f} GB")

    # 토크나이저 다운로드
    logger.info("Downloading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            token=token,
            trust_remote_code=True
        )
        logger.info("✓ Tokenizer downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to download tokenizer: {e}")
        return False

    # 모델 다운로드 (가중치만, 메모리 로드는 하지 않음)
    logger.info("Downloading model weights (this may take 10-30 minutes)...")
    logger.info("Note: Model will be ~22GB, ensure you have enough disk space")

    try:
        # download_only 모드로 다운로드만 수행
        AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            token=token,
            trust_remote_code=True,
            torch_dtype=torch.float16 if cuda_available else torch.float32,
            low_cpu_mem_usage=True,  # CPU 메모리 사용 최소화
            device_map=None  # 다운로드만 하고 로드는 하지 않음
        )
        logger.info("✓ Model downloaded successfully")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False

    # 다운로드 경로 출력
    if cache_dir:
        model_path = Path(cache_dir) / f"models--{model_name.replace('/', '--')}"
    else:
        model_path = Path.home() / ".cache" / "huggingface" / "hub" / f"models--{model_name.replace('/', '--')}"

    logger.info(f"\n✓ Download complete!")
    logger.info(f"Model location: {model_path}")
    logger.info(f"\nYou can now use the model with:")
    logger.info(f"  python scripts/test_llm_inference.py")

    return True


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Download EEVE-Korean-10.8B model from HuggingFace"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yanolja/EEVE-Korean-10.8B-v1.0",
        help="HuggingFace model ID (default: yanolja/EEVE-Korean-10.8B-v1.0)"
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Custom cache directory (default: ~/.cache/huggingface)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="HuggingFace API token (for private models)"
    )

    args = parser.parse_args()

    # 환경변수에서 토큰 가져오기 (명령줄 인자가 우선)
    token = args.token or os.getenv("HUGGINGFACE_TOKEN")

    # 다운로드 실행
    success = download_model(
        model_name=args.model,
        cache_dir=args.cache_dir,
        token=token
    )

    if success:
        logger.info("\n=== Download completed successfully! ===")
        sys.exit(0)
    else:
        logger.error("\n=== Download failed! ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
