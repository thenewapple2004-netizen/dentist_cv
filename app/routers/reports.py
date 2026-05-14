from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.quiz import Quiz, QuizAttempt
from app.routers.deps import get_current_user, require_faculty

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/faculty/overview")
def faculty_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_faculty),
):
    total_students = db.query(User).filter(User.role == "student").count()
    total_quizzes = db.query(Quiz).count()
    total_attempts = db.query(QuizAttempt).count()
    avg_score = db.query(func.avg(QuizAttempt.score)).scalar() or 0

    return {
        "total_students": total_students,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "average_score": round(float(avg_score), 1),
    }


@router.get("/faculty/students")
def student_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_faculty),
):
    students = db.query(User).filter(User.role == "student").all()
    result = []
    for s in students:
        attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == s.id).all()
        avg = sum(a.score for a in attempts) / len(attempts) if attempts else 0
        result.append({
            "id": s.id,
            "full_name": s.full_name,
            "email": s.email,
            "total_attempts": len(attempts),
            "average_score": round(avg, 1),
        })
    return result


@router.get("/faculty/quiz/{quiz_id}")
def quiz_performance(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_faculty),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return {"error": "Quiz not found"}
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    scores = [a.score for a in attempts]
    return {
        "quiz_title": quiz.title,
        "total_attempts": len(attempts),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "passing_rate": round(sum(1 for s in scores if s >= 60) / len(scores) * 100, 1) if scores else 0,
    }


@router.get("/student/my-progress")
def my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.asc())
        .all()
    )
    history = [
        {
            "attempt_id": a.id,
            "quiz_id": a.quiz_id,
            "score": a.score,
            "total_questions": a.total_questions,
            "time_taken_sec": a.time_taken_sec,
            "completed_at": a.completed_at,
        }
        for a in attempts
    ]
    scores = [a.score for a in attempts]
    return {
        "total_attempts": len(attempts),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "history": history,
    }
