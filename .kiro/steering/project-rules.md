---
inclusion: always
---

# Project Rules for Trajectory Engine MVP

## Critical Rule: No Changes Without Permission

**RULE:** Do not change, modify, install, or execute anything without explicitly asking the user first.

This includes:
- ❌ Do NOT install packages or dependencies
- ❌ Do NOT pull new models (ollama pull)
- ❌ Do NOT modify existing code files
- ❌ Do NOT execute commands that change system state
- ❌ Do NOT restart services
- ❌ Do NOT modify configuration files
- ❌ Do NOT delete files

**What you CAN do without asking:**
- ✅ Read files
- ✅ Create NEW documentation files
- ✅ Create NEW test scripts (but don't run them)
- ✅ Provide recommendations and suggestions
- ✅ Answer questions
- ✅ Explain concepts

**When suggesting changes:**
1. Explain what the change does
2. Explain why it's beneficial
3. Ask for explicit permission
4. Wait for user confirmation
5. Only then proceed with the change

**Example - CORRECT approach:**
```
I recommend installing the quantized model for 2-3x faster performance.

Command: ollama pull llama3.1:8b-instruct-q4_0

Benefits:
- 2-3x faster inference
- 50% less memory
- Minimal quality loss

Would you like me to run this command?
```

**Example - INCORRECT approach:**
```
Let me install the quantized model...
[Runs command without asking]
```

## Project-Specific Rules

### 1. Requirements are Final
- Do NOT modify requirements.md without explicit request
- Requirements are approved and locked
- Any changes must go through formal review

### 2. Testing Protocol
- Create test scripts but ASK before running them
- Explain what the test does before execution
- Get permission for any command that takes >5 seconds

### 3. Documentation
- You MAY create new documentation files freely
- You MAY update documentation with new information
- You MUST ask before modifying existing workflow documents

### 4. Code Generation
- You MAY create new code files as examples
- You MUST ask before modifying existing code
- You MUST ask before executing any code

### 5. System Changes
- ALWAYS ask before installing anything
- ALWAYS ask before changing configuration
- ALWAYS ask before restarting services

## Consequences of Breaking Rules

Breaking these rules will:
- Disrupt the user's workflow
- Potentially break their system
- Waste time undoing changes
- Reduce trust in the AI assistant

## When in Doubt

**If you're unsure whether something requires permission: ASK FIRST.**

It's better to ask unnecessarily than to make unwanted changes.
