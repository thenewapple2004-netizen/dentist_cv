"""
Run this once to create the database and seed demo accounts.
Usage: python scripts/init_db.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, SessionLocal, Base
from app.models import *
from app.core.security import hash_password


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Demo student
        if not db.query(User).filter(User.email == "student@demo.com").first():
            db.add(User(
                full_name="Ahmad Raza (Demo Student)",
                email="student@demo.com",
                hashed_password=hash_password("demo1234"),
                role="student",
            ))
            print("Created demo student: student@demo.com / demo1234")

        # Demo faculty
        if not db.query(User).filter(User.email == "faculty@demo.com").first():
            db.add(User(
                full_name="Dr. Sana Khan (Demo Faculty)",
                email="faculty@demo.com",
                hashed_password=hash_password("demo1234"),
                role="faculty",
            ))
            print("Created demo faculty: faculty@demo.com / demo1234")

        db.commit()

        # Seed sample quizzes (run after commit so faculty user is available)
        from app.services.quiz_service import SAMPLE_QUESTIONS, save_quiz
        faculty = db.query(User).filter(User.role == "faculty").first()
        if faculty and db.query(Quiz).count() == 0:
            for topic, questions in SAMPLE_QUESTIONS.items():
                title = topic.replace("_", " ").title() + " — Fundamentals"
                save_quiz(db, title, topic, questions, faculty.id)
                print(f"Created quiz: {title}")

        print("\nDatabase initialized successfully!")
        print("Run: uvicorn app.main:app --reload --port 8000")
    finally:
        db.close()


if __name__ == "__main__":
    main()
