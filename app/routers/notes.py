from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.notes import Bookmark, Note
from app.routers.deps import get_current_user

router = APIRouter(prefix="/api/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str
    content: str
    topic: Optional[str] = None


class BookmarkCreate(BaseModel):
    topic: str
    description: Optional[str] = None
    url_or_ref: Optional[str] = None


@router.post("/create")
def create_note(data: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = Note(user_id=current_user.id, title=data.title, content=data.content, topic=data.topic)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "title": note.title, "message": "Note saved"}


@router.get("/list")
def list_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notes = db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.updated_at.desc()).all()
    return [{"id": n.id, "title": n.title, "topic": n.topic, "content": n.content, "updated_at": n.updated_at} for n in notes]


@router.get("/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}")
def update_note(note_id: int, data: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = data.title
    note.content = data.content
    note.topic = data.topic
    db.commit()
    db.refresh(note)
    return {"message": "Note updated"}


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}


@router.post("/bookmark")
def add_bookmark(data: BookmarkCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bm = Bookmark(user_id=current_user.id, topic=data.topic, description=data.description, url_or_ref=data.url_or_ref)
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return {"id": bm.id, "topic": bm.topic, "message": "Bookmarked"}


@router.get("/bookmarks/list")
def list_bookmarks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bms = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    return bms
