from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # student | faculty
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    notes = relationship("Note", back_populates="user")
    uploaded_pdfs = relationship("UploadedPDF", back_populates="uploader")
    cv_analyses = relationship("CVAnalysisResult", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
