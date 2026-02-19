"""
Export student analysis to CSV for Notion import
"""

import json
import csv

print("📊 Exporting student analysis to CSV for Notion...")

# Read JSON data
with open('all_students_analysis.json', 'r', encoding='utf-8') as f:
    students = json.load(f)

# Write CSV
with open('students_for_notion.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'Name', 'GPA', 'Major', 'Trajectory Score', 
        'Placement Likelihood', 'Academic Score', 'Behavioral Score', 
        'Skills Score', 'Status'
    ])
    
    writer.writeheader()
    
    for student in students:
        writer.writerow({
            'Name': student['name'],
            'GPA': student['gpa'],
            'Major': student['major'],
            'Trajectory Score': student['trajectory_score'] if student['trajectory_score'] else 'N/A',
            'Placement Likelihood': student['placement_likelihood'] if student['placement_likelihood'] else 'N/A',
            'Academic Score': student['academic'] if student['academic'] else 'N/A',
            'Behavioral Score': student['behavioral'] if student['behavioral'] else 'N/A',
            'Skills Score': student['skills'] if student['skills'] else 'N/A',
            'Status': 'Not Placed'
        })

print(f"✅ Created students_for_notion.csv with {len(students)} students")
print()
print("To import to Notion:")
print("1. Open Notion")
print("2. Create a new database (Table)")
print("3. Click '...' → 'Import' → 'CSV'")
print("4. Select 'students_for_notion.csv'")
print("5. Done!")
