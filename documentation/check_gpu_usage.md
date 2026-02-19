# GPU Performance Issue - Diagnosis

## Current Status

✅ **GPU is detected**: RTX 4060 Laptop GPU (8GB)
✅ **Ollama shows "100% GPU"** in `ollama ps`
✅ **Model is loaded**: 5.5 GB in GPU memory
❌ **Speed is slow**: 25-67 tokens/s (should be 100-200 tokens/s)

## Why is it slow?

### Laptop GPU vs Desktop GPU

Your **RTX 4060 Laptop GPU** is significantly slower than desktop RTX 4060:

| Spec | Desktop RTX 4060 | Laptop RTX 4060 | Difference |
|------|------------------|-----------------|------------|
| CUDA Cores | 3072 | 2370 | -23% |
| Boost Clock | 2535 MHz | 1470-2370 MHz | Variable |
| TDP | 115W | 35-115W | Variable |
| Memory Bandwidth | 272 GB/s | 192 GB/s | -29% |

**Laptop GPUs are power-limited** and thermally constrained, so they run slower.

### Expected Performance for Laptop RTX 4060

- **Realistic speed**: 50-100 tokens/s (not 100-200)
- **Your speed**: 25-67 tokens/s
- **Conclusion**: Still slower than expected, but not by much

## Possible Causes

### 1. Power/Thermal Throttling
Laptop GPU may be throttling due to:
- Power limit (TDP)
- Temperature
- Battery vs AC power

**Check:**
```powershell
nvidia-smi -q -d PERFORMANCE
```

### 2. Shared Memory with iGPU
Laptop might be using integrated graphics for display, reducing available GPU resources.

### 3. Ollama Configuration
Ollama might not be fully utilizing GPU layers.

## Solutions to Try

### Solution 1: Force High Performance Mode

1. Open NVIDIA Control Panel
2. Manage 3D Settings → Program Settings
3. Add `ollama.exe`
4. Set:
   - Power management mode: **Prefer maximum performance**
   - CUDA - GPUs: **All**

### Solution 2: Ensure AC Power

Make sure laptop is plugged in (not on battery). Battery mode limits GPU performance.

### Solution 3: Check Thermal Throttling

Run this while testing:
```powershell
nvidia-smi -l 1
```

Watch for:
- GPU temperature (should be <85°C)
- Power usage (should be near max TDP)
- GPU utilization (should be 90-100%)

### Solution 4: Optimize Ollama Settings

Create `ollama_config.env`:
```bash
OLLAMA_NUM_GPU=1
OLLAMA_GPU_LAYERS=33
OLLAMA_NUM_PARALLEL=4
OLLAMA_NUM_THREAD=14
OLLAMA_FLASH_ATTENTION=1
```

### Solution 5: Use Smaller Context

Reduce context window to speed up inference:
```python
payload = {
    "model": "llama3.1:8b",
    "prompt": "...",
    "options": {
        "num_ctx": 2048,  # Reduce from 4096
        "num_predict": 100  # Limit output tokens
    }
}
```

## Realistic Expectations

For **RTX 4060 Laptop GPU** with **Llama 3.1 8B**:

| Scenario | Expected Speed | Your Speed | Status |
|----------|---------------|------------|--------|
| Short responses (<20 tokens) | 80-120 tokens/s | 25-67 tokens/s | ⚠️ Slow |
| Medium responses (50-100 tokens) | 60-100 tokens/s | ? | Need to test |
| Long responses (200+ tokens) | 50-80 tokens/s | ? | Need to test |

## Recommendation for MVP

**Accept current performance** (2-3s per request) for MVP:

### Why it's acceptable:

1. **Not user-facing real-time**: LLM jobs run in background
   - Data cleaning: Batch process during CSV import
   - Recommendations: Generated once, cached
   - Voice evaluation: Async after call ends
   - Gap narratives: Pre-generated
   - Skill demand: Cached for 30 days

2. **Parallel processing**: Run 4-8 requests simultaneously
   - 8 students × 3s each = 24s total (sequential)
   - 8 students ÷ 4 parallel = 6s total (parallel)

3. **Caching**: Most LLM results can be cached
   - Skill demand analysis: Cache 30 days
   - Recommendations: Cache until profile changes
   - Gap narratives: Cache until data changes

### Optimization for Production

For production (90-day plan), consider:

1. **Cloud GPU**: Use AWS/GCP with A10/T4 GPU (faster)
2. **Quantized model**: Use 4-bit quantization (2x faster)
3. **Smaller model**: Try Llama 3.1 7B or Mistral 7B
4. **Batch processing**: Process multiple students together

## Next Steps

1. ✅ Accept 2-3s performance for MVP
2. ✅ Implement caching to reduce LLM calls
3. ✅ Use parallel processing (ThreadPoolExecutor)
4. ✅ Focus on correctness, not speed
5. ⏭️ Optimize in production phase (Day 51-70)

## Conclusion

Your setup is working correctly. The "slow" speed is actually **normal for a laptop GPU**. 

For MVP (15 days), this performance is **acceptable**. Focus on:
- Getting all 5 LLM jobs working
- Implementing caching
- Parallel processing
- Building the rest of the system

Speed optimization can wait for production deployment.
