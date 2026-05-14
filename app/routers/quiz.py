from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.quiz import Quiz, QuizAttempt
from app.routers.deps import get_current_user, require_faculty
from app.schemas.quiz import (
    QuizOut, QuizAttemptSubmit, QuizAttemptOut,
    GenerateQuizRequest, SampleQuizRequest,
)
from app.services.quiz_service import (
    generate_quiz_from_text, save_quiz, submit_quiz_attempt,
    get_sample_quiz, DENTAL_TOPICS,
)
from app.services.pdf_service import get_pdf_text

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.get("/topics")
def list_topics():
    return DENTAL_TOPICS


@router.post("/sample")
async def get_sample(req: SampleQuizRequest, current_user: User = Depends(get_current_user)):
    questions = await get_sample_quiz(req.topic, req.num_questions)
    return {"title": f"Sample Quiz: {req.topic.replace('_', ' ').title()}", "questions": questions}


@router.post("/generate")
async def generate_quiz(
    req: GenerateQuizRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text = get_pdf_text(req.pdf_id, db)
    if not text.strip():
        raise HTTPException(status_code=400, detail="PDF has no extractable text")
    questions = await generate_quiz_from_text(text, req.num_questions, req.topic or "oral_pathology")
    quiz = save_quiz(
        db=db,
        title=req.topic or f"Quiz from PDF #{req.pdf_id}",
        topic=req.topic,
        questions=questions,
        created_by=current_user.id,
        pdf_id=req.pdf_id,
    )
    return QuizOut.model_validate(quiz)


@router.get("/list", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).limit(50).all()
    return quizzes


@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/submit", response_model=QuizAttemptOut)
def submit_quiz(
    data: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return submit_quiz_attempt(db, data.quiz_id, current_user.id, data.answers, data.time_taken_sec)


@router.get("/my/attempts", response_model=List[QuizAttemptOut])
def my_attempts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(20)
        .all()
    )
    return attempts
