from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(150))
    source_pdf_id = Column(Integer, ForeignKey("uploaded_pdfs.id"), nullable=True)
    questions = Column(JSON, nullable=False)   # list of question dicts
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    attempts = relationship("QuizAttempt", back_populates="quiz")
    source_pdf = relationship("UploadedPDF", back_populates="quizzes")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    answers = Column(JSON)     # {question_index: chosen_option}
    time_taken_sec = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")


class UploadedPDF(Base):
    __tablename__ = "uploaded_pdfs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    topic = Column(String(150))
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    uploader = relationship("User", back_populates="uploaded_pdfs")
    quizzes = relationship("Quiz", back_populates="source_pdf")
