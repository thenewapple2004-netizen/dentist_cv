import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.quiz import UploadedPDF
from app.config import UPLOAD_DIR

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    if not PDFPLUMBER_AVAILABLE:
        return ""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


async def save_uploaded_pdf(
    file: UploadFile,
    topic: str,
    uploader_id: int,
    db: Session,
) -> UploadedPDF:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = UPLOAD_DIR / unique_name

    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted_text = extract_text_from_pdf(str(dest_path))

    record = UploadedPDF(
        filename=unique_name,
        original_name=file.filename,
        topic=topic,
        file_path=str(dest_path),
        extracted_text=extracted_text,
        uploader_id=uploader_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_pdf_text(pdf_id: int, db: Session) -> str:
    record = db.query(UploadedPDF).filter(UploadedPDF.id == pdf_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="PDF not found")
    return record.extracted_text or ""
