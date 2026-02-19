"""
Quick GPU test for Ollama
"""
import requests
import json
import time

def test_with_gpu_monitoring():
    """Test LLM and monitor GPU usage"""
    
    print("Testing Ollama GPU usage...")
    print("\nBefore running LLM request:")
    print("Check nvidia-smi in another terminal - GPU should be idle\n")
    
    input("Press Enter to start LLM request (watch GPU usage in nvidia-smi)...")
    
    # Simple, fast request
    payload = {
        "model": "llama3.1:8b",
        "prompt": "Say 'Hello' and nothing else.",
        "stream": False,
        "options": {
            "num_predict": 10,
            "temperature": 0.1
        }
    }
    
    print("\nSending request to Ollama...")
    start = time.time()
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )
    
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Response: {result.get('response')}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"🔢 Tokens: {result.get('eval_count', 0)}")
        print(f"⚡ Tokens/sec: {result.get('eval_count', 0) / result.get('eval_duration', 1) * 1e9:.1f}")
        
        # Check if GPU was used
        if duration < 0.5:
            print("\n✅ FAST! Likely using GPU")
        elif duration < 1.5:
            print("\n⚠️  Moderate speed - might be using GPU")
        else:
            print("\n❌ SLOW! Likely using CPU only")
            print("\nTroubleshooting:")
            print("1. Check if CUDA is installed: nvidia-smi")
            print("2. Restart Ollama: Stop it and run 'ollama serve'")
            print("3. Check Ollama logs for GPU detection")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    test_with_gpu_monitoring()
