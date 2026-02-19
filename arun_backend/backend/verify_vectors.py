import sys
import os
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db import SessionLocal
from app.models import VectorProfile, Student

def show_stored_vectors():
    db = SessionLocal()
    profiles = db.query(VectorProfile).all()
    
    print(f"Found {len(profiles)} vector profiles in PostgreSQL.\n")
    
    for p in profiles:
        student_name = db.query(Student).filter(Student.id == p.student_id).first().name
        print(f"Student: {student_name}")
        if p.embedding_vector:
            print(f"Vector Stored? YES (Length: {len(p.embedding_vector)})")
            print(f"First 5 numbers: {p.embedding_vector[:5]}")
        else:
            print("Vector Stored? NO")
        print("-" * 30)

if __name__ == "__main__":
    show_stored_vectors()
