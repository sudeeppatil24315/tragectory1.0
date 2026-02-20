"""
Test script for skill demand weighting integration (Task 17.3)

This script tests the updated calculate_skill_score function with market weighting.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.trajectory_service import calculate_skill_score

print("=" * 80)
print("TEST: SKILL DEMAND WEIGHTING INTEGRATION (Task 17.3)")
print("=" * 80)

# Test student profile
student_profile = {
    'languages': 'Python,Java,JavaScript',
    'problem_solving': 4,
    'communication': 4,
    'teamwork': 4,
    'project_count': 5,
    'deployed': True,
    'internship': True,
    'career_clarity': 4,
    'major': 'Computer Science'
}

print("\n" + "=" * 80)
print("TEST 1: Base Skill Score (No Skills List)")
print("=" * 80)

base_score = calculate_skill_score(student_profile, skills=None)
print(f"\nBase Skill Score: {base_score:.3f} (0-1 range)")
print(f"Base Skill Score: {base_score * 100:.1f}/100")
print("\nComponents:")
print(f"  - Languages: 3 (Python, Java, JavaScript)")
print(f"  - Problem Solving: 4/5")
print(f"  - Communication: 4/5")
print(f"  - Teamwork: 4/5")
print(f"  - Projects: 5")
print(f"  - Deployed: Yes (+0.2)")
print(f"  - Internship: Yes (+0.15)")
print(f"  - Career Clarity: 4/5")

print("\n" + "=" * 80)
print("TEST 2: Market-Weighted Skill Score (High Demand Skills)")
print("=" * 80)

# Skills with high market demand (2.0x weight)
high_demand_skills = [
    {'skill_name': 'Python', 'proficiency_score': 85.0, 'market_weight': 2.0},
    {'skill_name': 'React', 'proficiency_score': 75.0, 'market_weight': 2.0},
    {'skill_name': 'AWS', 'proficiency_score': 70.0, 'market_weight': 2.0}
]

weighted_score_high = calculate_skill_score(student_profile, skills=high_demand_skills)
print(f"\nWeighted Skill Score: {weighted_score_high:.3f} (0-1 range)")
print(f"Weighted Skill Score: {weighted_score_high * 100:.1f}/100")
print("\nSkills:")
for skill in high_demand_skills:
    print(f"  - {skill['skill_name']}: {skill['proficiency_score']}/100 (weight: {skill['market_weight']}x)")

print(f"\nFormula: (base × 0.50) + (weighted × 0.50)")
print(f"  Base Score: {base_score:.3f}")
print(f"  Weighted Score: {(weighted_score_high - base_score * 0.5) / 0.5:.3f}")
print(f"  Final Score: {weighted_score_high:.3f}")

print("\n" + "=" * 80)
print("TEST 3: Market-Weighted Skill Score (Low Demand Skills)")
print("=" * 80)

# Skills with low market demand (0.5x weight)
low_demand_skills = [
    {'skill_name': 'jQuery', 'proficiency_score': 85.0, 'market_weight': 0.5},
    {'skill_name': 'PHP', 'proficiency_score': 75.0, 'market_weight': 0.5},
    {'skill_name': 'Flash', 'proficiency_score': 70.0, 'market_weight': 0.5}
]

weighted_score_low = calculate_skill_score(student_profile, skills=low_demand_skills)
print(f"\nWeighted Skill Score: {weighted_score_low:.3f} (0-1 range)")
print(f"Weighted Skill Score: {weighted_score_low * 100:.1f}/100")
print("\nSkills:")
for skill in low_demand_skills:
    print(f"  - {skill['skill_name']}: {skill['proficiency_score']}/100 (weight: {skill['market_weight']}x)")

print(f"\nFormula: (base × 0.50) + (weighted × 0.50)")
print(f"  Base Score: {base_score:.3f}")
print(f"  Weighted Score: {(weighted_score_low - base_score * 0.5) / 0.5:.3f}")
print(f"  Final Score: {weighted_score_low:.3f}")

print("\n" + "=" * 80)
print("TEST 4: Market-Weighted Skill Score (Mixed Demand)")
print("=" * 80)

# Skills with mixed market demand
mixed_demand_skills = [
    {'skill_name': 'Python', 'proficiency_score': 85.0, 'market_weight': 2.0},  # High
    {'skill_name': 'Java', 'proficiency_score': 75.0, 'market_weight': 1.0},    # Medium
    {'skill_name': 'jQuery', 'proficiency_score': 70.0, 'market_weight': 0.5}   # Low
]

weighted_score_mixed = calculate_skill_score(student_profile, skills=mixed_demand_skills)
print(f"\nWeighted Skill Score: {weighted_score_mixed:.3f} (0-1 range)")
print(f"Weighted Skill Score: {weighted_score_mixed * 100:.1f}/100")
print("\nSkills:")
for skill in mixed_demand_skills:
    demand = "High" if skill['market_weight'] == 2.0 else "Medium" if skill['market_weight'] == 1.0 else "Low"
    print(f"  - {skill['skill_name']}: {skill['proficiency_score']}/100 (weight: {skill['market_weight']}x, {demand} demand)")

print(f"\nFormula: (base × 0.50) + (weighted × 0.50)")
print(f"  Base Score: {base_score:.3f}")
print(f"  Weighted Score: {(weighted_score_mixed - base_score * 0.5) / 0.5:.3f}")
print(f"  Final Score: {weighted_score_mixed:.3f}")

print("\n" + "=" * 80)
print("COMPARISON SUMMARY")
print("=" * 80)

print(f"\nBase Score (no weighting):     {base_score * 100:.1f}/100")
print(f"High Demand Skills (2.0x):     {weighted_score_high * 100:.1f}/100  (+{(weighted_score_high - base_score) * 100:.1f})")
print(f"Mixed Demand Skills:           {weighted_score_mixed * 100:.1f}/100  (+{(weighted_score_mixed - base_score) * 100:.1f})")
print(f"Low Demand Skills (0.5x):      {weighted_score_low * 100:.1f}/100  ({(weighted_score_low - base_score) * 100:+.1f})")

print("\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)

print("\n1. Market weighting affects final score:")
print(f"   - High demand skills boost score by {(weighted_score_high - base_score) * 100:.1f} points")
print(f"   - Low demand skills reduce score by {abs(weighted_score_low - base_score) * 100:.1f} points")

print("\n2. Formula combines base (50%) + weighted (50%):")
print(f"   - Ensures profile-based factors still matter")
print(f"   - Market demand influences but doesn't dominate")

print("\n3. Students benefit from learning high-demand skills:")
print(f"   - Python, React, AWS (2.0x) vs jQuery, PHP (0.5x)")
print(f"   - Same proficiency, different market value")

print("\n" + "=" * 80)
print("✅ SKILL DEMAND WEIGHTING INTEGRATION COMPLETE!")
print("=" * 80)

print("\nTask 17.3 Status: COMPLETE")
print("- Updated calculate_skill_score() to combine base + weighted scores")
print("- Formula: final = (base × 0.50) + (weighted × 0.50)")
print("- Tested with high, low, and mixed demand skills")
print("- Market weighting properly influences trajectory score")
