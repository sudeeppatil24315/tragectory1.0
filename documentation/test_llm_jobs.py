"""
Test script for all 5 LLM jobs in Trajectory Engine MVP
Tests Ollama + Llama 3.1 8B integration
"""

import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def test_ollama_connection():
    """Test 1: Verify Ollama server is running"""
    print("\n" + "="*60)
    print("TEST 1: Ollama Connection")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama server is running")
            print(f"✅ Available models: {[m['name'] for m in models]}")
            return True
        else:
            print("❌ Ollama server returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def call_llm(prompt, system_prompt="", temperature=0.7, max_tokens=500):
    """Helper function to call Ollama API"""
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt
    
    start_time = time.time()
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        duration = time.time() - start_time
        
        return {
            "success": True,
            "response": result.get("response", ""),
            "duration": duration,
            "tokens": result.get("eval_count", 0)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

def test_job1_data_cleaning():
    """Test LLM Job #1: Data Cleaning"""
    print("\n" + "="*60)
    print("TEST 2: LLM Job #1 - Data Cleaning")
    print("="*60)
    
    system_prompt = """You are a data cleaning assistant. Clean and standardize data.
Return ONLY valid JSON with this format:
{
  "major": "cleaned major name",
  "gpa": normalized_gpa_float,
  "skills": ["cleaned", "skill", "names"]
}"""
    
    prompt = """Clean this student data:
- Major: comp sci
- GPA: 3.5 (on 4.0 scale)
- Skills: ReactJS, pyton, node.js

Return cleaned data as JSON."""
    
    print("Input: comp sci, GPA 3.5, Skills: ReactJS, pyton, node.js")
    print("Testing...")
    
    result = call_llm(prompt, system_prompt, temperature=0.1, max_tokens=300)
    
    if result["success"]:
        print(f"✅ Success! Duration: {result['duration']:.2f}s, Tokens: {result['tokens']}")
        print(f"Response:\n{result['response']}")
        
        # Try to parse JSON
        try:
            cleaned = json.loads(result['response'])
            print(f"✅ Valid JSON parsed")
            print(f"   Major: {cleaned.get('major')}")
            print(f"   GPA: {cleaned.get('gpa')}")
            print(f"   Skills: {cleaned.get('skills')}")
        except:
            print("⚠️  Response is not valid JSON (may need prompt tuning)")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_job2_recommendations():
    """Test LLM Job #2: Recommendation Generation"""
    print("\n" + "="*60)
    print("TEST 3: LLM Job #2 - Recommendations")
    print("="*60)
    
    system_prompt = """You are a career counselor. Generate 3 actionable recommendations.
Format each as:
**[Priority] Title**
- Action: specific steps
- Impact: +X points
- Timeline: timeframe"""
    
    prompt = """Generate recommendations for this student:
- Major: Computer Science
- GPA: 7.2/10
- Attendance: 78%
- Study Hours: 15/week
- Screen Time: 9 hours/day
- Trajectory Score: 62/100

Generate 3 recommendations to improve employability."""
    
    print("Input: CS student, GPA 7.2, Low attendance, High screen time")
    print("Testing...")
    
    result = call_llm(prompt, system_prompt, temperature=0.7, max_tokens=800)
    
    if result["success"]:
        print(f"✅ Success! Duration: {result['duration']:.2f}s, Tokens: {result['tokens']}")
        print(f"Response:\n{result['response']}")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_job3_voice_evaluation():
    """Test LLM Job #3: Voice Assessment Evaluation"""
    print("\n" + "="*60)
    print("TEST 4: LLM Job #3 - Voice Evaluation")
    print("="*60)
    
    system_prompt = """You are a technical interviewer. Score answers on 4 dimensions (0-10 each).
Return ONLY valid JSON:
{
  "technical_accuracy": score,
  "communication_clarity": score,
  "depth": score,
  "completeness": score,
  "overall_score": average_0_to_100
}"""
    
    prompt = """Evaluate this answer:

Question: Explain the difference between a list and tuple in Python.

Answer: A list is mutable, you can change it. A tuple is immutable, you cannot change it. Lists use square brackets, tuples use parentheses.

Score this answer (0-10 for each dimension)."""
    
    print("Input: Python question about lists vs tuples")
    print("Testing...")
    
    result = call_llm(prompt, system_prompt, temperature=0.3, max_tokens=400)
    
    if result["success"]:
        print(f"✅ Success! Duration: {result['duration']:.2f}s, Tokens: {result['tokens']}")
        print(f"Response:\n{result['response']}")
        
        try:
            scores = json.loads(result['response'])
            print(f"✅ Valid JSON parsed")
            print(f"   Technical Accuracy: {scores.get('technical_accuracy')}/10")
            print(f"   Communication: {scores.get('communication_clarity')}/10")
            print(f"   Overall Score: {scores.get('overall_score')}/100")
        except:
            print("⚠️  Response is not valid JSON (may need prompt tuning)")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_job4_gap_narrative():
    """Test LLM Job #4: Gap Analysis Narratives"""
    print("\n" + "="*60)
    print("TEST 5: LLM Job #4 - Gap Narratives")
    print("="*60)
    
    system_prompt = """You are a career counselor creating motivating narratives.
Explain gaps in a supportive, data-driven way."""
    
    prompt = """Create a gap analysis narrative:

Gap: Sleep Duration
Student's Value: 5.5 hours
Alumni Average: 7.2 hours
Gap: 24% below average

Write 3-4 sentences explaining why this matters and how to improve."""
    
    print("Input: Sleep gap (5.5 vs 7.2 hours)")
    print("Testing...")
    
    result = call_llm(prompt, system_prompt, temperature=0.7, max_tokens=600)
    
    if result["success"]:
        print(f"✅ Success! Duration: {result['duration']:.2f}s, Tokens: {result['tokens']}")
        print(f"Response:\n{result['response']}")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_job5_skill_demand():
    """Test LLM Job #5: Skill Market Demand Analysis"""
    print("\n" + "="*60)
    print("TEST 6: LLM Job #5 - Skill Market Demand")
    print("="*60)
    
    system_prompt = """You are a job market analyst. Assign market weight to skills.
Return ONLY valid JSON:
{
  "skill": "skill_name",
  "market_weight": 0.5 or 1.0 or 2.0,
  "demand_level": "High" or "Medium" or "Low",
  "reasoning": "data-driven explanation"
}"""
    
    prompt = """Analyze market demand for this skill in 2026:

Skill: Python
Major: Computer Science

Assign weight (0.5x=Low, 1.0x=Medium, 2.0x=High) based on job market demand."""
    
    print("Input: Python skill demand analysis")
    print("Testing...")
    
    result = call_llm(prompt, system_prompt, temperature=0.2, max_tokens=300)
    
    if result["success"]:
        print(f"✅ Success! Duration: {result['duration']:.2f}s, Tokens: {result['tokens']}")
        print(f"Response:\n{result['response']}")
        
        try:
            analysis = json.loads(result['response'])
            print(f"✅ Valid JSON parsed")
            print(f"   Skill: {analysis.get('skill')}")
            print(f"   Market Weight: {analysis.get('market_weight')}x")
            print(f"   Demand Level: {analysis.get('demand_level')}")
        except:
            print("⚠️  Response is not valid JSON (may need prompt tuning)")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_performance():
    """Test LLM Performance"""
    print("\n" + "="*60)
    print("TEST 7: Performance Benchmark")
    print("="*60)
    
    print("Running 5 quick requests to test performance...")
    
    durations = []
    for i in range(5):
        result = call_llm(
            prompt=f"Say 'Test {i+1} complete' and nothing else.",
            temperature=0.1,
            max_tokens=50
        )
        if result["success"]:
            durations.append(result["duration"])
            print(f"  Request {i+1}: {result['duration']:.2f}s")
    
    if durations:
        avg_duration = sum(durations) / len(durations)
        print(f"\n✅ Average response time: {avg_duration:.2f}s")
        
        if avg_duration < 1.0:
            print("✅ Excellent performance (<1s)")
        elif avg_duration < 2.0:
            print("✅ Good performance (<2s)")
        else:
            print("⚠️  Slower than expected (>2s)")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TRAJECTORY ENGINE MVP - LLM TESTING SUITE")
    print("Testing Ollama + Llama 3.1 8B")
    print("="*60)
    
    # Test 1: Connection
    if not test_ollama_connection():
        print("\n❌ Cannot proceed - Ollama server not running")
        print("Start Ollama with: ollama serve")
        return
    
    # Test all 5 LLM jobs
    test_job1_data_cleaning()
    test_job2_recommendations()
    test_job3_voice_evaluation()
    test_job4_gap_narrative()
    test_job5_skill_demand()
    
    # Performance test
    test_performance()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("1. Review responses above")
    print("2. If JSON parsing fails, tune prompts")
    print("3. Check performance (<2s is good)")
    print("4. Proceed with backend integration")

if __name__ == "__main__":
    main()
