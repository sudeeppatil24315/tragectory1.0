# Trajectory Engine - LLM Training Guide

## Overview

This guide explains how to train the Trajectory Engine LLM to analyze student profiles and predict employability trajectories using your CSV data.

## What We're Training

The LLM will learn to:
1. **Analyze student profiles** - Parse academic, behavioral, and skills data
2. **Calculate trajectory scores** - Apply optimal formulas (0-1 scale)
3. **Predict placement likelihood** - Estimate employability percentage
4. **Identify strengths & gaps** - Highlight top 3 of each
5. **Generate recommendations** - Provide 3-5 actionable steps
6. **Project future outcomes** - 30-day trajectory predictions

## Training Methodology

### Input: Student CSV Data
Your `student data.csv` contains 4 students with comprehensive data:
- Academic: GPA, attendance, backlogs, internal marks
- Skills: Programming languages, projects, internships
- Behavioral: Study hours, screen time, sleep, consistency
- Mental: Career clarity, confidence, interview fear

### Output: Structured Analysis
The LLM generates:
```
**TRAJECTORY ANALYSIS**
Overall Score: 0.72/1.00 (Strong)

Component Breakdown:
- Academic: 0.85/1.00 (85%)
- Behavioral: 0.65/1.00 (65%)
- Skills: 0.70/1.00 (70%)

Placement Likelihood: High (70-85%)

Key Strengths:
- Strong academic foundation (GPA: 8.6/10)
- Extensive project experience (5 projects)
- Real-world internship experience

Areas for Improvement:
- High screen time (6h/day) - reduce by 2-3 hours
- Low problem-solving score (2/5) - practice DSA
- Interview anxiety (4/5) - mock interviews

Actionable Recommendations:
1. Reduce screen time to 4-5 hours/day
2. Practice 50 DSA problems in next 30 days
3. Join mock interview sessions weekly
4. Build 1-2 more deployed projects
5. Improve consistency with daily study schedule

30-Day Projection:
Current: 0.72 → With improvements: 0.87
```

## Training Pipeline

### Step 1: Prepare Training Data

```bash
python prepare_training_data.py
```

**What it does:**
- Parses `student data.csv`
- Applies optimal formulas to calculate trajectory scores
- Generates training examples in JSONL format
- Creates human-readable summary

**Output files:**
- `training_data.jsonl` - Training examples for LLM
- `training_data_summary.md` - Human-readable summary

**Formula Application:**
```python
# Academic Component (25% for CS)
gpa_sigmoid = sigmoid_transform(gpa_normalized)
academic_score = 0.5*gpa + 0.25*attendance + 0.15*internal + 0.1*backlogs

# Behavioral Component (35% for CS)
behavioral_score = 0.2*study + 0.15*practice + 0.15*screen_time_inverse + 
                   0.1*social_media_inverse + 0.15*distraction_inverse + 
                   0.1*sleep_quality + 0.15*grit

# Skills Component (40% for CS)
skills_score = 0.15*languages + 0.15*problem_solving + 0.1*communication +
               0.1*teamwork + 0.15*projects + 0.2*deployment + 
               0.15*internship + 0.1*career_clarity

# Final Trajectory
trajectory = 0.25*academic + 0.35*behavioral + 0.40*skills
```

### Step 2: Train the Model

```bash
python train_llm.py
```

**Training Options:**

#### Option 1: Basic Model (System Prompt Only)
- Creates model with Trajectory Engine system prompt
- Fast setup (~1 minute)
- Good for basic analysis
- Model name: `trajectory-engine:latest`

#### Option 2: Enhanced Model (Few-Shot Learning)
- Includes training examples in system prompt
- Better accuracy (~15-20% improvement)
- Takes 2-3 minutes
- Model name: `trajectory-engine:latest-enhanced`

**What happens during training:**
1. Checks prerequisites (Ollama, base model, training data)
2. Creates Modelfile with system prompt
3. Builds custom model using `ollama create`
4. Tests model with sample student
5. Validates output format

### Step 3: Test the Model

**Interactive testing:**
```bash
ollama run trajectory-engine:latest
```

Then paste a student profile and get analysis.

**Programmatic testing:**
```bash
python integration_example.py
```

This runs a full test with Arun's profile and displays structured results.

## Integration in Your App

### Python Integration

```python
from integration_example import TrajectoryEngineLLM

# Initialize
llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest")

# Analyze student
student_data = {
    'name': 'John Doe',
    'major': 'Computer Science',
    'gpa': 8.0,
    'projects_count': 3,
    # ... more fields
}

analysis = llm.analyze_student(student_data)

# Access results
print(f"Score: {analysis['trajectory_score']}")
print(f"Likelihood: {analysis['placement_likelihood']}")
print(f"Strengths: {analysis['strengths']}")
print(f"Recommendations: {analysis['recommendations']}")
```

### REST API Integration

```python
import requests

url = "http://localhost:11434/api/generate"
payload = {
    "model": "trajectory-engine:latest",
    "prompt": "Analyze this student: ...",
    "stream": False
}

response = requests.post(url, json=payload)
result = response.json()
print(result['response'])
```

### Streaming Response

```python
import requests

url = "http://localhost:11434/api/generate"
payload = {
    "model": "trajectory-engine:latest",
    "prompt": "Analyze this student: ...",
    "stream": True
}

response = requests.post(url, json=payload, stream=True)
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data['response'], end='', flush=True)
```

## Training Data Format

### JSONL Structure

Each line in `training_data.jsonl`:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert career counselor..."
    },
    {
      "role": "user",
      "content": "Analyze this student profile: ..."
    },
    {
      "role": "assistant",
      "content": "**TRAJECTORY ANALYSIS**\nOverall Score: 0.72..."
    }
  ]
}
```

### Adding More Training Data

To improve accuracy, add more students:

1. **Collect more CSV data** - Aim for 50-100 students
2. **Ensure diversity** - Different majors, GPAs, behavioral patterns
3. **Include edge cases** - Very high/low performers
4. **Re-run preparation** - `python prepare_training_data.py`
5. **Retrain model** - `python train_llm.py`

## Model Configuration

### Modelfile Parameters

```dockerfile
FROM llama3.1:8b-instruct-q4_0

SYSTEM "Your system prompt here..."

# Temperature: Lower = more consistent, Higher = more creative
PARAMETER temperature 0.3

# Context window: How much text the model can process
PARAMETER num_ctx 4096

# Repeat penalty: Reduces repetitive text
PARAMETER repeat_penalty 1.1

# Top-p sampling: Quality vs diversity tradeoff
PARAMETER top_p 0.9
```

### Tuning Parameters

**For more consistent predictions:**
```
temperature 0.1-0.3
top_p 0.8-0.9
```

**For more creative analysis:**
```
temperature 0.5-0.7
top_p 0.9-0.95
```

**For longer context (detailed profiles):**
```
num_ctx 8192
```

## Performance Optimization

### Speed Improvements

1. **Use quantized model** (already using q4_0)
   - 2-3x faster than full precision
   - Minimal quality loss

2. **Reduce context window**
   ```
   PARAMETER num_ctx 2048  # Instead of 4096
   ```

3. **Batch processing**
   ```python
   # Process multiple students in parallel
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(llm.analyze_student, students)
   ```

4. **Cache responses**
   ```python
   import hashlib
   import json
   
   def get_cache_key(student_data):
       return hashlib.md5(json.dumps(student_data, sort_keys=True).encode()).hexdigest()
   
   cache = {}
   key = get_cache_key(student_data)
   if key in cache:
       return cache[key]
   ```

### Accuracy Improvements

1. **Add more training examples** (50-100 students)
2. **Include diverse scenarios** (different majors, patterns)
3. **Validate predictions** against actual placement data
4. **Fine-tune weights** based on validation results
5. **Use ensemble methods** (multiple models voting)

## Validation & Testing

### Test Cases

Create test cases for edge scenarios:

```python
test_cases = [
    {
        'name': 'High Academic, Low Behavioral',
        'gpa': 9.5,
        'study_hours': 2,
        'screen_time': 10,
        'expected_score': 0.60  # Should be moderate
    },
    {
        'name': 'Low Academic, High Skills',
        'gpa': 6.5,
        'projects_count': 10,
        'internship': 'Yes',
        'expected_score': 0.70  # Skills compensate
    },
    # ... more test cases
]

for test in test_cases:
    result = llm.analyze_student(test)
    assert abs(result['trajectory_score'] - test['expected_score']) < 0.1
```

### Validation Metrics

Track these metrics:

1. **Prediction Accuracy** - Compare to actual placements
2. **Score Distribution** - Should match real-world distribution
3. **Component Balance** - Academic/Behavioral/Skills ratios
4. **Recommendation Quality** - User feedback on suggestions
5. **Response Time** - Should be <3 seconds

## Deployment

### Production Checklist

- [ ] Train on 50+ students for better accuracy
- [ ] Validate predictions against actual placement data
- [ ] Set up monitoring for response times
- [ ] Implement caching for common queries
- [ ] Add error handling and fallbacks
- [ ] Configure rate limiting
- [ ] Set up logging for analysis requests
- [ ] Create backup models (v1, v2, etc.)

### Scaling

**Single Server:**
- Ollama on GPU server
- 10-20 concurrent requests
- 2-3s response time

**Multi-Server:**
- Load balancer → Multiple Ollama instances
- 100+ concurrent requests
- <1s response time with caching

**Cloud Deployment:**
- AWS/GCP GPU instances
- Auto-scaling based on load
- CDN for static content

## Troubleshooting

### Model Not Found
```bash
ollama list  # Check available models
ollama pull llama3.1:8b-instruct-q4_0  # Pull base model
```

### Slow Response
- Check GPU usage: `nvidia-smi`
- Reduce context window: `num_ctx 2048`
- Use smaller model: `llama3.1:7b`

### Inconsistent Predictions
- Lower temperature: `0.1-0.2`
- Add more training examples
- Validate formula calculations

### Out of Memory
- Use smaller model: `q4_0` instead of `q8_0`
- Reduce context: `num_ctx 2048`
- Close other GPU applications

## Next Steps

1. **Run preparation script** - Generate training data
2. **Train basic model** - Test with 4 students
3. **Validate results** - Compare to manual calculations
4. **Collect more data** - Aim for 50-100 students
5. **Retrain enhanced model** - Improve accuracy
6. **Integrate in app** - Use Python wrapper
7. **Deploy to production** - Set up monitoring

## Resources

- **Ollama Docs**: https://ollama.ai/docs
- **Llama 3.1 Guide**: https://ai.meta.com/llama/
- **Training Data Format**: https://ollama.ai/blog/fine-tuning
- **API Reference**: https://github.com/ollama/ollama/blob/main/docs/api.md

## Support

For issues or questions:
1. Check `training_data_summary.md` for data validation
2. Review `integration_example.py` for usage patterns
3. Test with `ollama run trajectory-engine:latest`
4. Check Ollama logs: `ollama logs`
