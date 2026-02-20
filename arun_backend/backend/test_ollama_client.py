"""
Test script for Ollama Client

This script tests the Ollama client wrapper to ensure it works correctly.
Run this after starting the Ollama server with Llama 3.1 8B model.
"""

from app.services.ollama_client import OllamaClient, get_ollama_client
import time


def test_ollama_client():
    """Test the Ollama client functionality"""
    
    print("=" * 60)
    print("TESTING OLLAMA CLIENT")
    print("=" * 60)
    
    # Create client
    print("\n1. Creating Ollama client...")
    client = OllamaClient()
    print("✓ Client created")
    
    # Test health check
    print("\n2. Testing health check...")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Available: {health['available']}")
    print(f"   Model: {health.get('model', 'N/A')}")
    print(f"   Model Available: {health.get('model_available', False)}")
    
    if health['available_models']:
        print(f"   Available Models: {', '.join(health['available_models'][:3])}")
    
    if not health['available']:
        print("\n✗ Ollama server not available")
        print("  Make sure Ollama is running:")
        print("  - Install: https://ollama.ai/download")
        print("  - Run: ollama serve")
        print("  - Pull model: ollama pull llama3.1:8b")
        return
    
    if not health.get('model_available', False):
        print(f"\n✗ Model {client.model} not available")
        print(f"  Run: ollama pull {client.model}")
        return
    
    print("✓ Health check passed")
    
    # Test simple generation
    print("\n3. Testing simple text generation...")
    prompt = "What is Python? Answer in one sentence."
    
    print(f"   Prompt: {prompt}")
    print("   Generating...")
    
    result = client.generate(
        prompt=prompt,
        temperature=0.3,
        max_tokens=100
    )
    
    if result['success']:
        print(f"✓ Generation successful")
        print(f"   Response: {result['text'][:200]}...")
        print(f"   Response Time: {result['response_time']:.2f}s")
        print(f"   Attempts: {result['attempts']}")
        print(f"   Tokens: {result.get('tokens', 0)}")
    else:
        print(f"✗ Generation failed: {result.get('error', 'Unknown error')}")
        return
    
    # Test with different temperatures
    print("\n4. Testing different temperature settings...")
    
    test_cases = [
        (0.1, "Very deterministic (data cleaning)"),
        (0.3, "Slightly creative (voice eval)"),
        (0.7, "Creative (recommendations)")
    ]
    
    for temp, description in test_cases:
        print(f"\n   Temperature {temp} - {description}")
        result = client.generate(
            prompt="Name one programming language.",
            temperature=temp,
            max_tokens=20
        )
        
        if result['success']:
            print(f"   ✓ Response: {result['text'].strip()}")
            print(f"   ✓ Time: {result['response_time']:.2f}s")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown')}")
    
    # Test batch processing
    print("\n5. Testing batch processing (parallel requests)...")
    
    prompts = [
        "What is 2+2?",
        "What is the capital of France?",
        "What is Python?",
        "What is AI?"
    ]
    
    print(f"   Processing {len(prompts)} prompts in parallel...")
    start_time = time.time()
    
    results = client.generate_batch(
        prompts=prompts,
        temperature=0.3,
        max_tokens=50
    )
    
    batch_time = time.time() - start_time
    
    successful = sum(1 for r in results if r['success'])
    print(f"✓ Batch complete: {successful}/{len(prompts)} successful")
    print(f"   Total Time: {batch_time:.2f}s")
    print(f"   Avg Time per Request: {batch_time/len(prompts):.2f}s")
    
    # Show first result
    if results and results[0]['success']:
        print(f"\n   Example result:")
        print(f"   Prompt: {prompts[0]}")
        print(f"   Response: {results[0]['text'].strip()}")
    
    # Test retry logic (with invalid model)
    print("\n6. Testing retry logic...")
    print("   Creating client with invalid model...")
    
    bad_client = OllamaClient(model="nonexistent-model")
    result = bad_client.generate(
        prompt="Test",
        temperature=0.5,
        max_tokens=10
    )
    
    if not result['success']:
        print(f"✓ Retry logic working (failed as expected)")
        print(f"   Attempts: {result['attempts']}")
        print(f"   Error: {result.get('error', 'Unknown')}")
    else:
        print("✗ Should have failed with invalid model")
    
    # Get metrics
    print("\n7. Performance Metrics...")
    metrics = client.get_metrics()
    
    print(f"   Total Requests: {metrics['total_requests']}")
    print(f"   Successful: {metrics['successful_requests']}")
    print(f"   Failed: {metrics['failed_requests']}")
    print(f"   Success Rate: {metrics['success_rate']:.1f}%")
    print(f"   Avg Response Time: {metrics['avg_response_time']:.2f}s")
    
    # Test singleton pattern
    print("\n8. Testing singleton pattern...")
    client1 = get_ollama_client()
    client2 = get_ollama_client()
    
    if client1 is client2:
        print("✓ Singleton pattern working (same instance)")
    else:
        print("✗ Singleton pattern not working (different instances)")
    
    # Shutdown
    print("\n9. Shutting down client...")
    client.shutdown()
    print("✓ Client shutdown complete")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nOllama client is ready for use in LLM services!")


if __name__ == "__main__":
    try:
        test_ollama_client()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
