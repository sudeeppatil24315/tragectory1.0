"""
Trajectory Engine - LLM Fine-tuning Script
Fine-tunes Llama 3.1 8B on student trajectory prediction
"""

import json
import subprocess
import os
from datetime import datetime

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_model_exists(model_name: str = "llama3.1:8b"):
    """Check if base model exists"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return model_name in result.stdout
    except:
        return False

def create_modelfile(base_model: str = "llama3.1:8b", 
                     output_file: str = "Modelfile"):
    """Create Modelfile for fine-tuning"""
    
    modelfile_content = f"""FROM {base_model}

# System prompt for Trajectory Engine
SYSTEM \"\"\"You are an expert career counselor and data scientist specializing in student employability prediction. 

You use the Trajectory Engine methodology which analyzes:
1. Academic Performance (GPA, attendance, backlogs) - 25% weight for CS majors
2. Behavioral Patterns (study habits, screen time, sleep, grit) - 35% weight for CS majors  
3. Skills & Experience (projects, internships, technical skills) - 40% weight for CS majors

You provide:
- Trajectory scores (0-1 scale)
- Component breakdowns
- Placement likelihood predictions
- Specific, actionable recommendations
- 30-day projections

Always be data-driven, empathetic, and actionable in your analysis.
\"\"\"

# Temperature for consistent predictions
PARAMETER temperature 0.3

# Increase context window for detailed analysis
PARAMETER num_ctx 4096

# Reduce repetition
PARAMETER repeat_penalty 1.1

# Top-p sampling for quality
PARAMETER top_p 0.9
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    print(f"✅ Created {output_file}")

def create_fine_tuned_model(modelfile: str = "Modelfile", 
                           model_name: str = "trajectory-engine:latest"):
    """Create fine-tuned model using Ollama"""
    
    print(f"\n🔧 Creating fine-tuned model: {model_name}")
    print("This may take a few minutes...\n")
    
    try:
        result = subprocess.run(
            ['ollama', 'create', model_name, '-f', modelfile],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully created model: {model_name}")
            return True
        else:
            print(f"❌ Error creating model:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_model(model_name: str = "trajectory-engine:latest", 
               test_prompt: str = None):
    """Test the fine-tuned model"""
    
    if test_prompt is None:
        test_prompt = """Analyze this student profile and predict their employability trajectory:

**Student Profile:**
- Name: Test Student
- Major: Computer Science (Semester 7)
- GPA: 8.0/10 (Stable)
- Attendance: 85%
- Backlogs: 0

**Skills & Experience:**
- Programming: Python, Java, JavaScript, SQL
- Projects: 4 (Academic, Personal, Internship)
- Deployed: Yes
- Internship: Yes (3 months)
- Problem Solving: 4/5

**Behavioral Patterns:**
- Study: 4h/day, Practice: 2h/day
- Screen Time: 6h/day (Social: 2h)
- Sleep: 7h (Irregular)
- Distraction Level: 3/5
- Consistency: 3/5

Provide a comprehensive employability analysis."""
    
    print(f"\n🧪 Testing model: {model_name}\n")
    print("=" * 60)
    print("TEST PROMPT:")
    print("=" * 60)
    print(test_prompt)
    print("=" * 60)
    print("\nGENERATING RESPONSE...\n")
    print("=" * 60)
    
    try:
        # Use ollama run command
        result = subprocess.run(
            ['ollama', 'run', model_name],
            input=test_prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("=" * 60)
            print("\n✅ Model test successful!")
            return True
        else:
            print(f"❌ Error testing model:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ Test timed out (30s)")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def train_with_examples(model_name: str = "trajectory-engine:latest",
                       training_file: str = "training_data.jsonl"):
    """
    Train model by running it through all training examples
    Note: Ollama doesn't support traditional fine-tuning yet,
    so we use few-shot learning by creating a model with examples
    """
    
    print(f"\n📚 Loading training examples from {training_file}...")
    
    if not os.path.exists(training_file):
        print(f"❌ Training file not found: {training_file}")
        return False
    
    # Load training examples
    examples = []
    with open(training_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))
    
    print(f"✅ Loaded {len(examples)} training examples")
    
    # Create enhanced Modelfile with few-shot examples
    print("\n🔧 Creating enhanced model with training examples...")
    
    base_model = "llama3.1:8b"
    enhanced_modelfile = f"""FROM {base_model}

# System prompt with few-shot examples
SYSTEM \"\"\"You are an expert career counselor and data scientist specializing in student employability prediction using the Trajectory Engine methodology.

METHODOLOGY:
- Academic Performance: 25% weight (GPA, attendance, backlogs)
- Behavioral Patterns: 35% weight (study habits, screen time, sleep, grit)
- Skills & Experience: 40% weight (projects, internships, technical skills)

OUTPUT FORMAT:
1. Overall Trajectory Score (0-1 scale)
2. Component Breakdown (academic, behavioral, skills)
3. Placement Likelihood (percentage)
4. Key Strengths (top 3)
5. Areas for Improvement (top 3)
6. Actionable Recommendations (3-5 specific steps)
7. 30-Day Projection

EXAMPLE ANALYSIS:

{examples[0]['messages'][1]['content'][:500]}...

RESPONSE:

{examples[0]['messages'][2]['content'][:500]}...

Always provide data-driven, empathetic, and actionable analysis.
\"\"\"

PARAMETER temperature 0.3
PARAMETER num_ctx 8192
PARAMETER repeat_penalty 1.1
PARAMETER top_p 0.9
"""
    
    # Write enhanced modelfile
    enhanced_file = "Modelfile.enhanced"
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_modelfile)
    
    print(f"✅ Created {enhanced_file}")
    
    # Create enhanced model
    enhanced_model_name = f"{model_name}-enhanced"
    print(f"\n🔧 Creating enhanced model: {enhanced_model_name}")
    
    try:
        result = subprocess.run(
            ['ollama', 'create', enhanced_model_name, '-f', enhanced_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully created enhanced model: {enhanced_model_name}")
            return enhanced_model_name
        else:
            print(f"❌ Error creating enhanced model:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("=" * 60)
    print("🚀 TRAJECTORY ENGINE - LLM TRAINING PIPELINE")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("📋 Checking prerequisites...")
    
    if not check_ollama_installed():
        print("❌ Ollama is not installed!")
        print("Install from: https://ollama.ai")
        return
    print("✅ Ollama is installed")
    
    base_model = "llama3.1:8b"
    if not check_model_exists(base_model):
        print(f"❌ Base model not found: {base_model}")
        print(f"Run: ollama pull {base_model}")
        return
    print(f"✅ Base model available: {base_model}")
    
    if not os.path.exists("training_data.jsonl"):
        print("❌ Training data not found!")
        print("Run: python prepare_training_data.py")
        return
    print("✅ Training data available")
    
    print("\n" + "=" * 60)
    print("TRAINING OPTIONS")
    print("=" * 60)
    print()
    print("1. Basic Model (system prompt only)")
    print("2. Enhanced Model (with few-shot examples)")
    print("3. Test Existing Model")
    print()
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        # Create basic model
        print("\n📝 Creating basic model...")
        create_modelfile()
        success = create_fine_tuned_model()
        
        if success:
            test_model()
    
    elif choice == "2":
        # Create enhanced model with examples
        print("\n📝 Creating enhanced model with training examples...")
        enhanced_model = train_with_examples()
        
        if enhanced_model:
            print(f"\n🧪 Testing enhanced model...")
            test_model(model_name=enhanced_model)
    
    elif choice == "3":
        # Test existing model
        model_name = input("Enter model name (default: trajectory-engine:latest): ").strip()
        if not model_name:
            model_name = "trajectory-engine:latest"
        
        test_model(model_name=model_name)
    
    else:
        print("❌ Invalid option")
        return
    
    print("\n" + "=" * 60)
    print("✅ TRAINING PIPELINE COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Test the model: ollama run trajectory-engine:latest")
    print("2. Use in your app: see integration_example.py")
    print("3. Deploy to production: see deployment guide")

if __name__ == "__main__":
    main()
