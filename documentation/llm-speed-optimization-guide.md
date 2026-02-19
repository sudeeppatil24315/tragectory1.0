# LLM Speed Optimization Guide
**Goal:** Reduce response time from 2-3s to <1s

---

## Quick Wins (Immediate - No Cost)

### 1. Use Quantized Models (2-3x Faster)
**Current:** llama3.1:8b (full precision, 4.9 GB)  
**Switch to:** llama3.1:8b-q4_0 (4-bit quantized, 2.5 GB)

**Benefits:**
- 2-3x faster inference
- 50% less memory usage
- Minimal quality loss (<5%)

**How to implement:**
```bash
# Pull quantized model
ollama pull llama3.1:8b-instruct-q4_0

# Or create custom quantized model
ollama create llama3.1-fast --quantize q4_0
```

**Update your code:**
```python
payload = {
    "model": "llama3.1:8b-instruct-q4_0",  # Use quantized model
    "prompt": prompt,
    # ... rest of config
}
```

**Expected improvement:** 2.9s → 1.0-1.5s ✅

---

### 2. Reduce Token Limits (Instant)
**Current:** max_tokens=500-800  
**Optimized:** max_tokens=100-300

Most LLM responses don't need 500+ tokens. Reducing limits speeds up generation.

**Before:**
```python
# Data cleaning - 500 tokens (too much)
call_llm(prompt, max_tokens=500)  # 3s

# Recommendations - 800 tokens (too much)
call_llm(prompt, max_tokens=800)  # 5s
```

**After:**
```python
# Data cleaning - 150 tokens (enough)
call_llm(prompt, max_tokens=150)  # 1s

# Recommendations - 300 tokens (enough)
call_llm(prompt, max_tokens=300)  # 2s
```

**Expected improvement:** 30-50% faster ✅

---

### 3. Shorter Prompts (Instant)
**Current:** Long system prompts + verbose instructions  
**Optimized:** Concise prompts with clear structure

**Before (slow):**
```python
system_prompt = """You are a data cleaning assistant for a student career 
prediction system. Your job is to standardize and clean messy input data.

Rules:
1. Fix typos and variations in major names (e.g., "Comp Sci" → "Computer Science")
2. Normalize GPA to 10.0 scale (convert from 4.0 scale or percentage if needed)
3. Standardize skill names (e.g., "ReactJS", "React.js" → "React")
4. Trim whitespace and fix capitalization
5. Return ONLY valid JSON, no explanations
6. If data is already clean, return it unchanged

Output format:
{
  "major": "cleaned major name",
  "gpa": normalized_gpa_float,
  "skills": ["cleaned", "skill", "names"],
  "corrections_applied": number_of_corrections
}"""
```

**After (fast):**
```python
system_prompt = """Clean data. Return JSON only:
{"major": "str", "gpa": float, "skills": ["str"]}

Rules: Fix typos, normalize GPA to 10.0 scale, standardize skill names."""
```

**Expected improvement:** 10-20% faster ✅

---

### 4. Use Flash Attention (If Available)
Enable flash attention for faster inference:

```bash
# Set environment variable
set OLLAMA_FLASH_ATTENTION=1

# Restart Ollama
ollama serve
```

**Expected improvement:** 10-30% faster ✅

---

### 5. Reduce Context Window
**Current:** 4096 tokens context  
**Optimized:** 2048 tokens context

```python
payload = {
    "model": "llama3.1:8b",
    "prompt": prompt,
    "options": {
        "num_ctx": 2048,  # Reduce from 4096
        "num_predict": 150
    }
}
```

**Expected improvement:** 15-25% faster ✅

---

## Medium Effort (1-2 hours setup)

### 6. Use Smaller, Faster Models
Switch to smaller models for specific jobs:

**Option A: Llama 3.2 3B (3x faster)**
```bash
ollama pull llama3.2:3b-instruct-q4_0
```
- Size: 1.5 GB (vs 4.9 GB)
- Speed: 150-200 tokens/s (vs 50-70 tokens/s)
- Quality: Good for simple tasks (data cleaning, skill demand)

**Option B: Phi-3 Mini (4x faster)**
```bash
ollama pull phi3:mini
```
- Size: 2.3 GB
- Speed: 200+ tokens/s
- Quality: Excellent for structured tasks

**Use case mapping:**
```python
# Fast model for simple tasks
FAST_MODEL = "llama3.2:3b-instruct-q4_0"
SMART_MODEL = "llama3.1:8b-instruct-q4_0"

# Job #1: Data Cleaning → Use FAST_MODEL
# Job #2: Recommendations → Use SMART_MODEL
# Job #3: Voice Evaluation → Use SMART_MODEL
# Job #4: Gap Narratives → Use SMART_MODEL
# Job #5: Skill Demand → Use FAST_MODEL
```

**Expected improvement:** 2-4x faster for simple tasks ✅

---

### 7. Batch Processing with Parallel Requests
Process multiple students simultaneously:

```python
from concurrent.futures import ThreadPoolExecutor
import time

def process_student(student):
    """Process one student"""
    return generate_recommendations(student)

def process_batch(students, max_workers=4):
    """Process multiple students in parallel"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_student, students))
    return results

# Example: Process 8 students
students = [student1, student2, ..., student8]

# Sequential: 8 × 3s = 24s
start = time.time()
for student in students:
    process_student(student)
print(f"Sequential: {time.time() - start:.1f}s")  # 24s

# Parallel: 8 ÷ 4 workers = 2 batches × 3s = 6s
start = time.time()
process_batch(students, max_workers=4)
print(f"Parallel: {time.time() - start:.1f}s")  # 6s
```

**Expected improvement:** 4x throughput ✅

---

### 8. Implement Smart Caching
Cache LLM responses to avoid repeated calls:

```python
from functools import lru_cache
import hashlib
import json

# In-memory cache
@lru_cache(maxsize=1000)
def cached_skill_demand(skill_name: str, major: str):
    """Cache skill demand analysis for 30 days"""
    return analyze_skill_demand(skill_name, major)

# Redis cache (for production)
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def cached_llm_call(prompt: str, ttl: int = 3600):
    """Cache LLM responses in Redis"""
    # Create cache key
    cache_key = f"llm:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    # Check cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Call LLM
    result = call_llm(prompt)
    
    # Store in cache
    r.setex(cache_key, ttl, json.dumps(result))
    
    return result

# Usage
result = cached_llm_call(prompt, ttl=86400)  # Cache for 24 hours
```

**Cache strategy:**
- Skill demand analysis: 30 days
- Recommendations: Until profile changes
- Gap narratives: Until data changes
- Data cleaning: No cache (one-time)
- Voice evaluation: No cache (unique answers)

**Expected improvement:** 90% cache hit rate = 10x faster ✅

---

## Advanced Solutions (Requires Setup)

### 9. Use vLLM (10x Faster)
vLLM is an optimized inference engine for LLMs.

**Installation:**
```bash
pip install vllm
```

**Setup:**
```python
from vllm import LLM, SamplingParams

# Load model once
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9
)

# Fast inference
sampling_params = SamplingParams(
    temperature=0.7,
    max_tokens=300
)

outputs = llm.generate(prompts, sampling_params)
```

**Benefits:**
- 10-20x faster than Ollama
- Continuous batching
- PagedAttention for memory efficiency
- Better GPU utilization

**Expected improvement:** 2.9s → 0.2-0.5s ✅

---

### 10. Use TensorRT-LLM (15x Faster)
NVIDIA's optimized inference engine.

**Installation:**
```bash
# Requires CUDA 12.x
pip install tensorrt-llm
```

**Benefits:**
- 15-20x faster than standard inference
- Optimized for NVIDIA GPUs
- FP16/INT8 quantization
- Kernel fusion

**Expected improvement:** 2.9s → 0.15-0.3s ✅

---

### 11. Use Groq API (100x Faster)
Groq has custom LPU chips for ultra-fast inference.

**Setup:**
```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=300
)
```

**Benefits:**
- 500+ tokens/s (vs 50-70 tokens/s)
- <0.5s response time
- Free tier: 30 requests/min
- Paid: $0.05-0.10 per 1M tokens

**Cost comparison:**
- Local: $0 but slow (2-3s)
- Groq: ~$5/month for 1000 students but fast (<0.5s)

**Expected improvement:** 2.9s → 0.3-0.5s ✅

---

## Recommended Optimization Strategy

### Phase 1: Quick Wins (Today - Free)
1. ✅ Switch to quantized model (llama3.1:8b-q4_0)
2. ✅ Reduce max_tokens (500 → 150-300)
3. ✅ Shorten prompts
4. ✅ Enable flash attention
5. ✅ Reduce context window (4096 → 2048)

**Expected result:** 2.9s → 1.0-1.5s

---

### Phase 2: Smart Architecture (Week 1)
1. ✅ Use smaller models for simple tasks (Llama 3.2 3B)
2. ✅ Implement caching (Redis)
3. ✅ Parallel processing (ThreadPoolExecutor)
4. ✅ Keep model loaded in memory

**Expected result:** 1.5s → 0.5-1.0s (with 90% cache hits)

---

### Phase 3: Production Optimization (Days 51-70)
1. ✅ Deploy vLLM on cloud GPU (AWS g4dn.xlarge)
2. ✅ Use TensorRT-LLM for critical paths
3. ✅ Implement request batching
4. ✅ Load balancing across multiple GPUs

**Expected result:** 0.5s → 0.2-0.3s

---

### Phase 4: Consider Groq (If Budget Allows)
1. ✅ Use Groq API for real-time features
2. ✅ Keep local LLM for batch processing
3. ✅ Hybrid approach: Groq for speed, local for cost

**Expected result:** <0.5s for real-time, $5-10/month cost

---

## Implementation Priority

### Must Do (This Week)
```bash
# 1. Pull quantized model
ollama pull llama3.1:8b-instruct-q4_0

# 2. Pull smaller model for simple tasks
ollama pull llama3.2:3b-instruct-q4_0

# 3. Enable flash attention
set OLLAMA_FLASH_ATTENTION=1
ollama serve
```

### Should Do (Week 2)
```python
# 1. Implement caching
pip install redis
# Start Redis: redis-server

# 2. Reduce token limits in all LLM calls
max_tokens = 150  # Data cleaning
max_tokens = 300  # Recommendations
max_tokens = 200  # Voice evaluation
max_tokens = 250  # Gap narratives
max_tokens = 150  # Skill demand

# 3. Implement parallel processing
from concurrent.futures import ThreadPoolExecutor
```

### Nice to Have (Production)
```bash
# 1. Install vLLM
pip install vllm

# 2. Consider Groq API
# Sign up: https://console.groq.com
```

---

## Testing Script

Create `test_optimizations.py`:

```python
import time
import requests

def test_model(model_name, prompt, max_tokens=150):
    """Test inference speed"""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "num_ctx": 2048,
            "temperature": 0.1
        }
    }
    
    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        tokens = result.get('eval_count', 0)
        tokens_per_sec = tokens / (result.get('eval_duration', 1) / 1e9)
        
        return {
            "model": model_name,
            "duration": duration,
            "tokens": tokens,
            "tokens_per_sec": tokens_per_sec
        }
    return None

# Test different models
prompt = "Clean this data: major=comp sci, gpa=3.5, skills=ReactJS,pyton"

models = [
    "llama3.1:8b",                    # Current (slow)
    "llama3.1:8b-instruct-q4_0",     # Quantized (faster)
    "llama3.2:3b-instruct-q4_0",     # Smaller (fastest)
]

print("Model Comparison:")
print("="*60)

for model in models:
    result = test_model(model, prompt, max_tokens=150)
    if result:
        print(f"{model:30} | {result['duration']:.2f}s | {result['tokens_per_sec']:.0f} tok/s")

print("="*60)
```

---

## Expected Results After Optimization

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Quantized model | 2.9s | 1.2s | 2.4x faster |
| + Reduced tokens | 1.2s | 0.9s | 1.3x faster |
| + Shorter prompts | 0.9s | 0.8s | 1.1x faster |
| + Smaller model (simple tasks) | 0.8s | 0.4s | 2x faster |
| + Caching (90% hit rate) | 0.4s | 0.04s | 10x faster |
| **Total improvement** | **2.9s** | **0.04-0.8s** | **3-70x faster** |

---

## Conclusion

**Immediate action (today):**
1. Switch to quantized model: `ollama pull llama3.1:8b-instruct-q4_0`
2. Reduce max_tokens to 150-300
3. Enable flash attention

**Expected result:** 2.9s → 1.0-1.5s (2-3x faster)

**With caching (week 2):** 90% of requests will be <0.1s

**This is good enough for MVP!** Further optimization can wait for production phase.
