from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str


class QuizCreate(BaseModel):
    title: str
    topic: Optional[str] = None
    questions: List[QuizQuestion]
    source_pdf_id: Optional[int] = None


class QuizOut(BaseModel):
    id: int
    title: str
    topic: Optional[str]
    questions: List[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


class QuizAttemptSubmit(BaseModel):
    quiz_id: int
    answers: Dict[str, int]
    time_taken_sec: int = 0


class QuizAttemptOut(BaseModel):
    id: int
    quiz_id: int
    score: float
    total_questions: int
    time_taken_sec: int
    completed_at: datetime

    model_config = {"from_attributes": True}


class GenerateQuizRequest(BaseModel):
    pdf_id: int
    num_questions: int = 10
    topic: Optional[str] = None


class SampleQuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
