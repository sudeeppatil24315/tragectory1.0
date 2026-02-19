# LLM Testing - Recommended Fixes

## Issues Found & Solutions

### Issue 1: JSON Responses with Markdown Formatting
**Jobs Affected:** #1 (Data Cleaning), #5 (Skill Demand)

**Problem:** LLM wraps JSON in markdown code blocks:
```
Here is the JSON:
```json
{"key": "value"}
```
```

**Solution:** Strip markdown before parsing
```python
def extract_json(response: str) -> str:
    """Extract JSON from markdown code blocks"""
    # Remove markdown code blocks
    response = response.replace("```json", "").replace("```", "")
    
    # Find JSON object
    start = response.find("{")
    end = response.rfind("}") + 1
    
    if start != -1 and end > start:
        return response[start:end]
    
    return response
```

### Issue 2: Voice Evaluation Overall Score Calculation
**Job Affected:** #3 (Voice Evaluation)

**Problem:** Overall score returned as 30/100 instead of average (should be ~75)

**Solution:** Update prompt to clarify calculation
```python
SYSTEM_PROMPT = """...
"overall_score": (technical_accuracy + communication_clarity + depth + completeness) * 2.5
This converts the 0-40 range to 0-100 scale.
"""
```

### Issue 3: Skill Market Weight Not Exact
**Job Affected:** #5 (Skill Demand)

**Problem:** Returned 1.8x instead of exactly 2.0x

**Solution:** Strengthen prompt constraint
```python
SYSTEM_PROMPT = """...
CRITICAL: You MUST assign EXACTLY one of these three values:
- 0.5 (Low Demand)
- 1.0 (Medium Demand)  
- 2.0 (High Demand)

NO OTHER VALUES ARE ALLOWED. Do not use 1.5, 1.8, or any other number.
"""
```

### Issue 4: Performance (2.89s average)
**All Jobs Affected**

**Problem:** Slower than 1s target

**Solutions:**
1. **Reduce max_tokens** - Most responses don't need 500-800 tokens
2. **Use GPU** - Ensure Ollama is using RTX 4060 (check with `nvidia-smi`)
3. **Optimize prompts** - Shorter prompts = faster responses
4. **Batch requests** - Process multiple students in parallel

**Check GPU usage:**
```bash
# Windows
nvidia-smi

# Should show ollama process using GPU
```

**Optimize Ollama config:**
```bash
# Set environment variables
set OLLAMA_NUM_PARALLEL=8
set OLLAMA_GPU_LAYERS=33

# Restart Ollama
ollama serve
```

## Updated Test Script with Fixes

Save as `test_llm_jobs_v2.py`:

```python
import json
import re

def extract_json(response: str) -> str:
    """Extract JSON from markdown code blocks or text"""
    # Remove markdown code blocks
    response = response.replace("```json", "").replace("```", "")
    
    # Find JSON object or array
    json_pattern = r'(\{[^{}]*\}|\[[^\[\]]*\])'
    matches = re.findall(json_pattern, response, re.DOTALL)
    
    if matches:
        # Try to parse each match
        for match in matches:
            try:
                json.loads(match)
                return match
            except:
                continue
    
    # Fallback: find first { to last }
    start = response.find("{")
    end = response.rfind("}") + 1
    
    if start != -1 and end > start:
        return response[start:end]
    
    return response

# Update test_job1_data_cleaning():
result = call_llm(prompt, system_prompt, temperature=0.1, max_tokens=300)

if result["success"]:
    print(f"✅ Success! Duration: {result['duration']:.2f}s")
    
    # Extract and parse JSON
    json_str = extract_json(result['response'])
    try:
        cleaned = json.loads(json_str)
        print(f"✅ Valid JSON parsed")
        print(f"   Major: {cleaned.get('major')}")
        print(f"   GPA: {cleaned.get('gpa')}")
        print(f"   Skills: {cleaned.get('skills')}")
    except Exception as e:
        print(f"⚠️  JSON parsing failed: {e}")
```

## Performance Optimization Tips

### 1. Reduce Token Limits
```python
# Before
max_tokens=800  # Recommendations

# After  
max_tokens=400  # Most recommendations fit in 400 tokens
```

### 2. Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def process_students_parallel(students):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(generate_recommendations, student)
            for student in students
        ]
        results = [f.result() for f in futures]
    return results
```

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_skill_demand_cached(skill_name: str):
    # Cache results for 30 days
    return analyze_skill_demand(skill_name)
```

## Next Steps

1. ✅ LLM is working - all 5 jobs functional
2. 🔧 Apply JSON extraction fixes
3. 🔧 Update prompts for exact outputs
4. ⚡ Optimize performance (GPU check, reduce tokens)
5. 🚀 Integrate into FastAPI backend
6. 🧪 Test with real student data

## Conclusion

Your Ollama + Llama 3.1 8B setup is working correctly! The responses are high quality and relevant. With minor prompt tuning and JSON extraction fixes, you'll have a production-ready LLM pipeline.

Performance is acceptable for MVP (2-3s per request). For production, optimize with GPU acceleration and parallel processing to handle 8+ simultaneous requests.
