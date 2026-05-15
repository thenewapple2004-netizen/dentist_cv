import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.analysis import CVAnalysisResult
from app.routers.deps import get_current_user
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/api/cv", tags=["computer-vision"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

@router.post("/analyze")
async def analyze_dental_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported image format: {ext}")

    img_name = f"{uuid.uuid4().hex}{ext}"
    img_path = UPLOAD_DIR / img_name
    with img_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        from cv.dental_analyzer import analyze_image
        result = analyze_image(str(img_path))
        
        # Save to DB
        analysis_record = CVAnalysisResult(
            user_id=current_user.id,
            image_name=file.filename,
            condition_detected=result["predicted_condition"],
            confidence=result["confidence"],
            details=result.get("description", ""),
        )
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
    except Exception as e:
        img_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    img_path.unlink(missing_ok=True)
    return result


@router.get("/conditions")
def list_conditions():
    from cv.dental_analyzer import CONDITION_LABELS, CONDITION_INFO
    return [
        {
            "name": label,
            "severity": CONDITION_INFO[label]["severity"],
            "description": CONDITION_INFO[label]["description"],
        }
        for label in CONDITION_LABELS
    ]
