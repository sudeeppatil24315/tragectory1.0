"""
Quick test to compare optimization strategies
Run this to see immediate improvements
"""
import requests
import time

def test_optimization(description, model, max_tokens, num_ctx=4096):
    """Test a specific optimization"""
    prompt = "Say 'test complete' and nothing else."
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "num_ctx": num_ctx,
            "temperature": 0.1
        }
    }
    
    start = time.time()
    try:
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
            
            print(f"{description:40} | {duration:.2f}s | {tokens_per_sec:.0f} tok/s")
            return duration
        else:
            print(f"{description:40} | ERROR")
            return None
    except Exception as e:
        print(f"{description:40} | ERROR: {e}")
        return None

print("\n" + "="*70)
print("LLM OPTIMIZATION COMPARISON")
print("="*70)

# Test 1: Current setup (baseline)
print("\n1. BASELINE (Current Setup):")
baseline = test_optimization(
    "Current: llama3.1:8b, 500 tokens, 4096 ctx",
    model="llama3.1:8b",
    max_tokens=500,
    num_ctx=4096
)

# Test 2: Reduced tokens
print("\n2. OPTIMIZATION: Reduce max_tokens:")
opt1 = test_optimization(
    "Optimized: llama3.1:8b, 150 tokens, 4096 ctx",
    model="llama3.1:8b",
    max_tokens=150,
    num_ctx=4096
)

# Test 3: Reduced context
print("\n3. OPTIMIZATION: Reduce context window:")
opt2 = test_optimization(
    "Optimized: llama3.1:8b, 150 tokens, 2048 ctx",
    model="llama3.1:8b",
    max_tokens=150,
    num_ctx=2048
)

# Calculate improvements
print("\n" + "="*70)
print("RESULTS:")
print("="*70)

if baseline and opt1:
    improvement1 = (baseline - opt1) / baseline * 100
    print(f"Reducing tokens (500→150):     {improvement1:.1f}% faster")

if baseline and opt2:
    improvement2 = (baseline - opt2) / baseline * 100
    print(f"Reducing tokens + context:     {improvement2:.1f}% faster")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("\n1. Install quantized model (2-3x faster):")
print("   ollama pull llama3.1:8b-instruct-q4_0")
print("\n2. Install smaller model for simple tasks (4x faster):")
print("   ollama pull llama3.2:3b-instruct-q4_0")
print("\n3. Update your code to use optimized settings:")
print("   - max_tokens: 150-300 (not 500-800)")
print("   - num_ctx: 2048 (not 4096)")
print("   - Use quantized models")
print("\n4. Implement caching (90% cache hit = 10x faster)")
print("\n" + "="*70)
