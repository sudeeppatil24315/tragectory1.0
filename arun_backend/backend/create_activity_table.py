"""
STEP 2: Create the student_activities table in the database

What this script does:
1. Connects to your PostgreSQL database
2. Creates the new 'student_activities' table
3. Adds indexes for fast queries on student_id and date

Run this once to set up the table.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db import engine
from app.models import Base, StudentActivity

def create_activity_table():
    print("Creating student_activities table...")
    print("-" * 50)
    
    # This creates ONLY the StudentActivity table (not all tables)
    StudentActivity.__table__.create(bind=engine, checkfirst=True)
    
    print("[SUCCESS] Table 'student_activities' created successfully!")
    print("\nTable structure:")
    print("  - id (primary key)")
    print("  - student_id (links to students table)")
    print("  - date (which day)")
    print("  - title (activity name)")
    print("  - activity_type (schedule/todo/plan)")
    print("  - start_time, end_time (for scheduling)")
    print("  - is_completed (status)")
    print("  - priority (1=high, 2=medium, 3=low)")
    print("\nYou can now use this table for:")
    print("  - Daily Schedule")
    print("  - To-Do Lists")
    print("  - Day Planning")

if __name__ == "__main__":
    create_activity_table()
