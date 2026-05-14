from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.quiz import UploadedPDF
from app.routers.deps import get_current_user, require_faculty
from app.services.pdf_service import save_uploaded_pdf

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    topic: str = Form(default="General Oral Pathology"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_faculty),
):
    record = await save_uploaded_pdf(file, topic, current_user.id, db)
    return {
        "id": record.id,
        "original_name": record.original_name,
        "topic": record.topic,
        "text_length": len(record.extracted_text or ""),
        "message": "PDF uploaded and text extracted successfully",
    }


@router.get("/list")
def list_pdfs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdfs = db.query(UploadedPDF).order_by(UploadedPDF.uploaded_at.desc()).all()
    return [
        {
            "id": p.id,
            "original_name": p.original_name,
            "topic": p.topic,
            "uploaded_at": p.uploaded_at,
        }
        for p in pdfs
    ]


@router.get("/{pdf_id}")
def get_pdf_info(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf = db.query(UploadedPDF).filter(UploadedPDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {
        "id": pdf.id,
        "original_name": pdf.original_name,
        "topic": pdf.topic,
        "text_preview": (pdf.extracted_text or "")[:500],
        "uploaded_at": pdf.uploaded_at,
    }
