"""
Diagnose why Ollama is not using GPU properly
"""
import subprocess
import sys
import os

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

print("="*60)
print("OLLAMA GPU DIAGNOSTIC")
print("="*60)

# 1. Check NVIDIA GPU
print("\n1. Checking NVIDIA GPU...")
gpu_output = run_command("nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader")
print(f"GPU: {gpu_output.strip()}")

# 2. Check CUDA
print("\n2. Checking CUDA...")
cuda_output = run_command("nvcc --version")
if "release" in cuda_output.lower():
    print("✅ CUDA is installed")
    print(cuda_output)
else:
    print("❌ CUDA not found in PATH")
    print("This might be why Ollama is using CPU!")

# 3. Check Ollama version
print("\n3. Checking Ollama version...")
ollama_version = run_command("ollama --version")
print(f"Version: {ollama_version.strip()}")

# 4. Check environment variables
print("\n4. Checking Ollama environment variables...")
env_vars = [
    "OLLAMA_NUM_GPU",
    "OLLAMA_GPU_LAYERS", 
    "OLLAMA_NUM_PARALLEL",
    "OLLAMA_NUM_THREAD",
    "CUDA_VISIBLE_DEVICES"
]

for var in env_vars:
    value = os.environ.get(var, "Not set")
    print(f"   {var}: {value}")

# 5. Check if model is loaded
print("\n5. Checking loaded models...")
ps_output = run_command("ollama ps")
print(ps_output)

# 6. Run quick test
print("\n6. Running speed test...")
import time
import requests

payload = {
    "model": "llama3.1:8b",
    "prompt": "Say 'test' and nothing else.",
    "stream": False,
    "options": {"num_predict": 5}
}

start = time.time()
try:
    response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        tokens = result.get('eval_count', 0)
        eval_duration_ns = result.get('eval_duration', 1)
        tokens_per_sec = tokens / (eval_duration_ns / 1e9)
        
        print(f"   Duration: {duration:.2f}s")
        print(f"   Tokens generated: {tokens}")
        print(f"   Speed: {tokens_per_sec:.1f} tokens/s")
        
        if tokens_per_sec > 100:
            print("   ✅ FAST - Using GPU!")
        elif tokens_per_sec > 50:
            print("   ⚠️  MODERATE - Might be using GPU partially")
        else:
            print("   ❌ SLOW - Using CPU only!")
except Exception as e:
    print(f"   Error: {e}")

# 7. Recommendations
print("\n" + "="*60)
print("DIAGNOSIS & RECOMMENDATIONS")
print("="*60)

print("\nIssue: Ollama is running at ~57 tokens/s (CPU speed)")
print("Expected: 100-200 tokens/s on RTX 4060")

print("\nPossible causes:")
print("1. ❌ CUDA not installed or not in PATH")
print("2. ❌ Ollama not compiled with CUDA support")
print("3. ❌ Environment variables not set")
print("4. ❌ Model layers not loaded on GPU")

print("\nSolutions:")
print("\n1. Install CUDA Toolkit 12.x:")
print("   Download from: https://developer.nvidia.com/cuda-downloads")
print("   Make sure to add CUDA to PATH during installation")

print("\n2. Reinstall Ollama (Windows version with CUDA):")
print("   Download from: https://ollama.com/download/windows")
print("   The installer should detect CUDA automatically")

print("\n3. Set environment variables (after CUDA install):")
print("   Run these commands in PowerShell:")
print("   $env:OLLAMA_NUM_GPU=1")
print("   $env:OLLAMA_GPU_LAYERS=33")
print("   Then restart Ollama")

print("\n4. Verify GPU usage:")
print("   Run 'nvidia-smi' in another terminal while running LLM")
print("   You should see 'ollama' process using GPU memory")

print("\n5. Keep model loaded:")
print("   Run: ollama run llama3.1:8b")
print("   Keep this running to avoid reload time")

print("\n" + "="*60)
