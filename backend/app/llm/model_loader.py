"""
LLM 모델 로더 및 추론 서비스

EEVE-Korean-10.8B 모델을 로드하고 INT8 양자화를 적용하여
RTX 5070 TI (16GB VRAM)에서 효율적으로 실행합니다.
"""
import os
import logging
from typing import Optional, List, Dict, Any
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    GenerationConfig
)

logger = logging.getLogger(__name__)


class LLMModelLoader:
    """
    로컬 LLM 모델 로더 및 추론 클래스

    EEVE-Korean-10.8B를 INT8 양자화로 로드하여
    16GB VRAM에서 안정적으로 실행합니다.
    """

    def __init__(
        self,
        model_name: str = "yanolja/EEVE-Korean-10.8B-v1.0",
        device: str = "cuda",
        load_in_8bit: bool = True,
        use_flash_attention: bool = True
    ):
        """
        Args:
            model_name: HuggingFace 모델 ID
            device: 실행 디바이스 (cuda 또는 cpu)
            load_in_8bit: INT8 양자화 사용 여부 (VRAM 절약)
            use_flash_attention: Flash Attention 2 사용 (속도 향상)
        """
        self.model_name = model_name
        self.device = device
        self.load_in_8bit = load_in_8bit
        self.use_flash_attention = use_flash_attention

        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.generation_config: Optional[GenerationConfig] = None

        # CUDA 사용 가능 여부 확인
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available. Falling back to CPU.")
            self.device = "cpu"
            self.load_in_8bit = False  # CPU에서는 8bit 양자화 불가

    def load_model(self) -> None:
        """
        모델과 토크나이저를 메모리에 로드합니다.

        INT8 양자화를 사용하여 VRAM 사용량을 약 50% 절감합니다.
        (~22GB → ~11GB)
        """
        logger.info(f"Loading model: {self.model_name}")
        logger.info(f"Device: {self.device}, 8-bit: {self.load_in_8bit}")

        # 토크나이저 로드
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # 특수 토큰 설정
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 양자화 설정
        quantization_config = None
        if self.load_in_8bit and self.device == "cuda":
            logger.info("Configuring INT8 quantization...")
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,  # 양자화 임계값
                llm_int8_has_fp16_weight=False
            )

        # 모델 로드
        logger.info("Loading model (this may take a few minutes)...")
        model_kwargs = {
            "pretrained_model_name_or_path": self.model_name,
            "trust_remote_code": True,
            "device_map": "auto" if self.device == "cuda" else None,
            "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
        }

        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config

        if self.use_flash_attention and self.device == "cuda":
            try:
                model_kwargs["attn_implementation"] = "flash_attention_2"
                logger.info("Using Flash Attention 2")
            except Exception as e:
                logger.warning(f"Flash Attention 2 not available: {e}")

        self.model = AutoModelForCausalLM.from_pretrained(**model_kwargs)

        # CPU 모드에서는 수동으로 디바이스 이동
        if self.device == "cpu":
            self.model = self.model.to(self.device)

        # 평가 모드로 전환 (dropout 비활성화)
        self.model.eval()

        # 기본 생성 설정
        self.generation_config = GenerationConfig(
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        logger.info("Model loaded successfully!")

        # VRAM 사용량 출력 (CUDA만)
        if self.device == "cuda":
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"VRAM Usage - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")

    def is_loaded(self) -> bool:
        """모델이 로드되었는지 확인"""
        return self.model is not None and self.tokenizer is not None

    def unload_model(self) -> None:
        """모델을 메모리에서 해제"""
        if self.model is not None:
            del self.model
            self.model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        if self.device == "cuda":
            torch.cuda.empty_cache()

        logger.info("Model unloaded from memory")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
        **kwargs
    ) -> str:
        """
        텍스트 생성

        Args:
            prompt: 입력 프롬프트
            max_new_tokens: 생성할 최대 토큰 수
            temperature: 샘플링 온도 (0.0-2.0, 낮을수록 결정적)
            top_p: Nucleus sampling (0.0-1.0)
            top_k: Top-K sampling
            repetition_penalty: 반복 페널티 (1.0보다 크면 반복 억제)
            **kwargs: 추가 GenerationConfig 파라미터

        Returns:
            생성된 텍스트 (프롬프트 제외)
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # 입력 토크나이징
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048
        ).to(self.device)

        # 생성 설정 업데이트
        generation_config = GenerationConfig(
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            **kwargs
        )

        # 추론 실행
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=generation_config
            )

        # 디코딩 (프롬프트 부분 제외)
        input_length = inputs['input_ids'].shape[1]
        generated_tokens = outputs[0][input_length:]
        generated_text = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return generated_text.strip()

    def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> str:
        """
        시스템 프롬프트와 사용자 프롬프트를 결합하여 생성

        Args:
            system_prompt: 시스템 역할 정의 (예: "당신은 한국어 유머 작가입니다.")
            user_prompt: 사용자 요청
            **kwargs: generate() 메서드의 추가 파라미터

        Returns:
            생성된 텍스트
        """
        # 프롬프트 템플릿 구성
        full_prompt = f"""### System:
{system_prompt}

### User:
{user_prompt}

### Assistant:
"""

        return self.generate(full_prompt, **kwargs)

    def batch_generate(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """
        여러 프롬프트에 대해 배치 생성

        Args:
            prompts: 프롬프트 리스트
            **kwargs: generate() 메서드의 추가 파라미터

        Returns:
            생성된 텍스트 리스트
        """
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error generating for prompt: {e}")
                results.append("")

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보 반환

        Returns:
            모델 설정 및 상태 정보
        """
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "load_in_8bit": self.load_in_8bit,
            "use_flash_attention": self.use_flash_attention,
            "is_loaded": self.is_loaded(),
        }

        if self.is_loaded() and self.device == "cuda":
            info["vram_allocated_gb"] = torch.cuda.memory_allocated() / 1024**3
            info["vram_reserved_gb"] = torch.cuda.memory_reserved() / 1024**3

        return info


# 싱글톤 인스턴스 (메모리 절약)
_global_llm_instance: Optional[LLMModelLoader] = None


def get_llm_instance(auto_load: bool = False) -> LLMModelLoader:
    """
    글로벌 LLM 인스턴스를 반환합니다.

    싱글톤 패턴으로 메모리 사용을 최소화합니다.

    Args:
        auto_load: True면 모델이 로드되지 않았을 때 자동 로드

    Returns:
        LLMModelLoader 인스턴스
    """
    global _global_llm_instance

    if _global_llm_instance is None:
        _global_llm_instance = LLMModelLoader()

    if auto_load and not _global_llm_instance.is_loaded():
        _global_llm_instance.load_model()

    return _global_llm_instance
