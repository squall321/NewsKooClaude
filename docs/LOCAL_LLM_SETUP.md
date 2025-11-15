# 로컬 LLM 설정 가이드

> RTX 5070 TI (16GB VRAM)로 한국어 LLM을 실행하여 **API 비용 제로** 달성하기

## 목차
1. [개요](#개요)
2. [시스템 요구사항](#시스템-요구사항)
3. [CUDA 환경 설정](#cuda-환경-설정)
4. [모델 선택 가이드](#모델-선택-가이드)
5. [모델 다운로드 및 설치](#모델-다운로드-및-설치)
6. [vLLM 설정](#vllm-설정)
7. [Flask 통합](#flask-통합)
8. [성능 최적화](#성능-최적화)
9. [문제 해결](#문제-해결)

---

## 개요

### 왜 로컬 LLM인가?

**비용 절감**:
- OpenAI GPT-4: $0.03/1K tokens (출력 기준)
- 월 10,000개 재구성 시: **~$300/월**
- 로컬 LLM: **$0** (전기 비용 ~$5/월)

**장점**:
- ✅ API 비용 제로
- ✅ 속도 제어 가능 (배치 처리)
- ✅ 데이터 프라이버시 (외부 전송 없음)
- ✅ 오프라인 작동 가능

**단점**:
- ⚠️ 초기 설정 복잡
- ⚠️ VRAM 요구사항
- ⚠️ 품질이 GPT-4보다 낮을 수 있음 (하지만 충분히 좋음)

---

## 시스템 요구사항

### 하드웨어 (최소)
- **GPU**: NVIDIA RTX 5070 TI (16GB VRAM) ✅
- **RAM**: 16GB 시스템 메모리
- **저장공간**: 30GB (모델 저장용)
- **CPU**: 멀티코어 권장

### 하드웨어 (권장)
- **GPU**: RTX 5070 TI / RTX 4090
- **RAM**: 32GB+
- **저장공간**: 100GB (여러 모델 실험)
- **CPU**: AMD Ryzen 7+ / Intel i7+

### 소프트웨어
- **OS**: Ubuntu 22.04 / Windows 11 (WSL2)
- **Python**: 3.10 or 3.11
- **CUDA**: 12.1+
- **cuDNN**: 8.9+
- **PyTorch**: 2.1+

---

## CUDA 환경 설정

### 1. NVIDIA 드라이버 설치 (Linux)

```bash
# 현재 드라이버 확인
nvidia-smi

# 드라이버가 없다면 설치
sudo apt update
sudo apt install nvidia-driver-535  # 버전은 상황에 맞게
sudo reboot

# 설치 확인
nvidia-smi
```

**출력 예시**:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.86.10    Driver Version: 535.86.10    CUDA Version: 12.2   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
| 30%   35C    P8    15W / 285W |    512MiB / 16384MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### 2. CUDA Toolkit 설치

```bash
# CUDA 12.1 설치 (Ubuntu)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# 환경 변수 설정
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 설치 확인
nvcc --version
```

### 3. PyTorch 설치 (CUDA 지원)

```bash
cd backend
python -m venv venv
source venv/bin/activate

# PyTorch 2.1 + CUDA 12.1
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# 설치 확인
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
```

**예상 출력**:
```
CUDA available: True
Device: NVIDIA GeForce RTX 5070 Ti
```

---

## 모델 선택 가이드

### 추천 한국어 LLM 모델

| 모델 | 크기 | VRAM (FP16) | VRAM (INT8) | 속도 | 품질 | 추천도 |
|------|------|-------------|-------------|------|------|--------|
| **EEVE-Korean-10.8B** | 10.8B | 22GB | **12GB** | 중 | ⭐⭐⭐⭐⭐ | 🥇 최고 |
| Llama-3-Open-Ko-8B | 8B | 16GB | **9GB** | 빠름 | ⭐⭐⭐⭐ | 🥈 대체안 |
| Mistral-7B-Korean | 7B | 14GB | **8GB** | 빠름 | ⭐⭐⭐ | 🥉 경량 |
| Polyglot-Ko-12.8B | 12.8B | 26GB | 14GB | 느림 | ⭐⭐⭐⭐ | ❌ VRAM 초과 |

**결론**: **EEVE-Korean-10.8B (INT8 양자화)** 사용 권장
- RTX 5070 TI 16GB에 완벽히 맞음
- 한국어 품질 최고
- 유머 재구성에 적합

### EEVE-Korean-10.8B 특징
- **개발자**: 야놀자 (Yanolja)
- **기반 모델**: Llama-3
- **특화**: 한국어 자연스러운 생성
- **라이선스**: Llama 3 Community License (상업적 이용 가능)
- **HuggingFace**: `yanolja/EEVE-Korean-10.8B-v1.0`

---

## 모델 다운로드 및 설치

### 1. HuggingFace CLI 설치

```bash
cd backend
source venv/bin/activate

pip install huggingface-hub[cli]
pip install transformers accelerate bitsandbytes
```

### 2. 모델 다운로드

**옵션 A: 자동 다운로드 (권장)**

```bash
# backend/scripts/download_model.py 생성
mkdir -p scripts
cat > scripts/download_model.py << 'EOF'
from huggingface_hub import snapshot_download
import os

MODEL_ID = "yanolja/EEVE-Korean-10.8B-v1.0"
MODEL_DIR = "./models/EEVE-Korean-10.8B"

print(f"Downloading {MODEL_ID}...")
print(f"This will take ~20 minutes (14GB download)")

os.makedirs(MODEL_DIR, exist_ok=True)

snapshot_download(
    repo_id=MODEL_ID,
    local_dir=MODEL_DIR,
    local_dir_use_symlinks=False,
    resume_download=True
)

print(f"✅ Model downloaded to {MODEL_DIR}")
EOF

# 실행
python scripts/download_model.py
```

**옵션 B: CLI로 직접 다운로드**

```bash
huggingface-cli download yanolja/EEVE-Korean-10.8B-v1.0 \
  --local-dir ./models/EEVE-Korean-10.8B \
  --local-dir-use-symlinks False
```

### 3. 모델 양자화 (INT8)

**VRAM을 12GB로 줄이기**

```bash
# backend/scripts/quantize_model.py 생성
cat > scripts/quantize_model.py << 'EOF'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os

MODEL_PATH = "./models/EEVE-Korean-10.8B"
QUANTIZED_PATH = "./models/EEVE-Korean-10.8B-INT8"

print("🔧 Quantizing model to INT8...")

# INT8 양자화 설정
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False
)

# 모델 로드 (INT8)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# 저장
os.makedirs(QUANTIZED_PATH, exist_ok=True)
model.save_pretrained(QUANTIZED_PATH)
tokenizer.save_pretrained(QUANTIZED_PATH)

print(f"✅ Quantized model saved to {QUANTIZED_PATH}")
print(f"VRAM usage reduced: 22GB → 12GB")
EOF

# 실행 (약 10분 소요)
python scripts/quantize_model.py
```

---

## vLLM 설정

### vLLM이란?
- **빠른 추론 엔진**: HuggingFace보다 2-5배 빠름
- **PagedAttention**: 메모리 효율적
- **배치 처리**: 여러 요청 동시 처리

### 설치

```bash
pip install vllm
```

### vLLM 서버 시작

```bash
# backend/scripts/start_vllm_server.sh 생성
cat > scripts/start_vllm_server.sh << 'EOF'
#!/bin/bash

MODEL_PATH="./models/EEVE-Korean-10.8B-INT8"
PORT=8000

echo "🚀 Starting vLLM server on port $PORT..."

python -m vllm.entrypoints.openai.api_server \
  --model $MODEL_PATH \
  --port $PORT \
  --dtype float16 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85 \
  --tensor-parallel-size 1
EOF

chmod +x scripts/start_vllm_server.sh

# 서버 시작
./scripts/start_vllm_server.sh
```

**출력 예시**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### vLLM 테스트

```bash
# 다른 터미널에서 실행
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "./models/EEVE-Korean-10.8B-INT8",
    "prompt": "다음 영어 유머를 한국 스타일로 재구성해줘:\nWhy did the programmer quit his job? Because he didn'\''t get arrays.",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

---

## Flask 통합

### 1. LLM 모델 로더

```python
# backend/app/llm/model_loader.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional
import os

class LLMModelLoader:
    _instance: Optional['LLMModelLoader'] = None

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self, model_path: str):
        """모델 로드 (서버 시작 시 한 번만)"""
        if self.model is not None:
            print("✅ Model already loaded")
            return

        print(f"🔄 Loading model from {model_path}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )

        print(f"✅ Model loaded on {self.device}")
        print(f"📊 VRAM usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

    def generate(self, prompt: str, max_length: int = 512, temperature: float = 0.7):
        """텍스트 생성"""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
```

### 2. 프롬프트 템플릿

```python
# backend/app/llm/prompts.py

REWRITE_HUMOR_PROMPT = """당신은 전문 유머 작가입니다. 다음 해외 유머의 핵심 아이디어를 파악하고, 한국 독자가 이해하기 쉽게 재구성해주세요.

**중요 규칙**:
1. 원본을 단순 번역하지 말고, 아이디어를 차용하여 새롭게 창작
2. 한국 문화 맥락에 맞게 수정 (예: 미국 → 한국, 달러 → 원)
3. 유머의 핵심 포인트 유지
4. 자연스러운 한국어 사용
5. 원본과의 유사도는 70% 이하로

**원본 유머**:
{original_text}

**재구성 요구사항**:
- 스타일: {style}  (예: 캐주얼, 격식, 유머러스)
- 길이: {length}  (예: 짧게, 중간, 길게)

**재구성된 유머**:
"""

TITLE_GENERATION_PROMPT = """다음 유머 글을 읽고, 클릭하고 싶게 만드는 매력적인 제목을 3개 생성해주세요.

**글 내용**:
{content}

**제목 요구사항**:
- 15-30자 길이
- 호기심 유발
- SEO 키워드 포함
- 클릭베이트지만 과하지 않게

**제목 (3개)**:
1.
2.
3.
"""

IMPROVE_PARAGRAPH_PROMPT = """다음 문단을 더 나은 품질로 개선해주세요.

**원본**:
{paragraph}

**개선 요청**:
- {improvement_type}  (예: 명확성 향상, 유머 추가, 톤 변경)

**개선된 문단**:
"""
```

### 3. AI 재구성 서비스

```python
# backend/app/services/ai_rewriter.py
from app.llm.model_loader import LLMModelLoader
from app.llm.prompts import REWRITE_HUMOR_PROMPT
from typing import List

class AIRewriter:
    def __init__(self):
        self.llm = LLMModelLoader.get_instance()

    def rewrite_humor(
        self,
        original_text: str,
        style: str = "캐주얼",
        length: str = "중간",
        num_versions: int = 3
    ) -> List[str]:
        """유머 재구성 (여러 버전 생성)"""

        results = []

        for i in range(num_versions):
            prompt = REWRITE_HUMOR_PROMPT.format(
                original_text=original_text,
                style=style,
                length=length
            )

            generated = self.llm.generate(
                prompt,
                max_length=1024,
                temperature=0.7 + (i * 0.1)  # 다양성 증가
            )

            # 프롬프트 부분 제거
            rewritten = generated.split("**재구성된 유머**:")[-1].strip()
            results.append(rewritten)

        return results

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """간단한 유사도 계산 (Jaccard)"""
        set1 = set(text1.split())
        set2 = set(text2.split())

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0
```

### 4. API 엔드포인트

```python
# backend/app/api/ai_assistant.py
from flask import Blueprint, request, jsonify
from app.services.ai_rewriter import AIRewriter

bp = Blueprint('ai', __name__, url_prefix='/api/v1/ai')
rewriter = AIRewriter()

@bp.route('/rewrite', methods=['POST'])
def rewrite_humor():
    """유머 재구성 API"""
    data = request.json

    original = data.get('original_text')
    style = data.get('style', '캐주얼')
    length = data.get('length', '중간')
    num_versions = data.get('num_versions', 3)

    if not original:
        return jsonify({'error': 'original_text is required'}), 400

    try:
        results = rewriter.rewrite_humor(
            original_text=original,
            style=style,
            length=length,
            num_versions=num_versions
        )

        # 원본과의 유사도 체크
        similarities = [
            rewriter.calculate_similarity(original, r)
            for r in results
        ]

        return jsonify({
            'success': True,
            'versions': [
                {
                    'text': text,
                    'similarity': sim,
                    'warning': sim > 0.7
                }
                for text, sim in zip(results, similarities)
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 성능 최적화

### 1. 배치 처리

```python
# 여러 요청을 한 번에 처리
def batch_rewrite(texts: List[str]) -> List[str]:
    prompts = [REWRITE_HUMOR_PROMPT.format(original_text=t) for t in texts]

    # vLLM의 배치 처리 활용
    results = llm.batch_generate(prompts, batch_size=4)
    return results
```

### 2. 캐싱

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def rewrite_with_cache(original_hash: str, style: str):
    # 동일한 요청은 캐시에서 반환
    return rewriter.rewrite_humor(original, style)
```

### 3. GPU 메모리 모니터링

```python
import torch

def log_gpu_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        print(f"GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
```

---

## 문제 해결

### CUDA Out of Memory

**증상**:
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**해결책**:
1. INT8 양자화 사용
2. `max_length` 줄이기
3. Batch size 줄이기
4. 모델 언로드 후 재로드

```python
# 메모리 정리
torch.cuda.empty_cache()
```

### 추론 속도 느림

**증상**: 한 번 생성에 30초+

**해결책**:
1. vLLM 사용 (2-5배 빠름)
2. `max_length` 줄이기 (512 → 256)
3. `torch.compile()` 사용 (PyTorch 2.0+)

```python
model = torch.compile(model)
```

### 모델 로딩 실패

**증상**:
```
OSError: Can't load model
```

**해결책**:
1. 모델 경로 확인
2. 권한 확인 (`chmod -R 755 models/`)
3. 디스크 공간 확인 (`df -h`)

---

## 다음 단계

1. ✅ 로컬 LLM 환경 구축 완료
2. 📝 프롬프트 튜닝 (Few-shot examples 추가)
3. 🧪 재구성 품질 테스트
4. 🔄 Flask API 통합
5. 🎨 관리자 UI 연동

**Phase 5 완료 후**: [Phase 6: AI 재구성 엔진](../DEVELOPMENT_ROADMAP.md#phase-6-ai-재구성-엔진---프롬프트-설계)로 이동하세요!

---

**참고 자료**:
- [vLLM 공식 문서](https://docs.vllm.ai/)
- [EEVE 모델 카드](https://huggingface.co/yanolja/EEVE-Korean-10.8B-v1.0)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
