import os
import sys
# Add backend directory to path to import app modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db import SessionLocal
from app.models import Student
from app.services.vector_gen_service import generate_and_store_student_vector

def vectorize_all():
    db = SessionLocal()
    students = db.query(Student).all()
    print(f"Vectorizing {len(students)} students...")
    success = 0
    fail = 0
    for s in students:
        try:
            print(f"Processing {s.name}...")
            # This call might crash if ChromaDB is broken on this system
            generate_and_store_student_vector(db, s.id)
            success += 1
        except Exception as e:
            print(f"Failed to vectorize {s.name}: {e}")
            fail += 1
    
    print(f"Vectorization Complete: {success} Success, {fail} Failed.")
    db.close()

if __name__ == "__main__":
    vectorize_all()
