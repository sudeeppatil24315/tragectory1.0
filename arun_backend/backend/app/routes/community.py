from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import CommunityPost
import shutil
import os
import uuid
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/community", tags=["community"])

# --- Pydantic Schemas ---
class CommunityPostResponse(BaseModel):
    id: int
    student_id: int
    media_url: str
    media_type: str
    caption: str
    likes_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Routes ---

@router.post("/upload", response_model=CommunityPostResponse)
async def upload_media(
    student_id: int = Form(...),
    media_type: str = Form(...), # 'meme' or 'reel'
    caption: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a meme or reel to the local file system and record it in the database.
    """
    # 1. Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "video/mp4", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported.")

    # 2. Create unique filename
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # 3. Define save path
    # Path relative to the app root for storage
    upload_dir = os.path.join("static", "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 4. Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # 5. Save metadata to Database
    # URL that the frontend will use to access the file
    media_url = f"/static/uploads/{unique_filename}"
    
    new_post = CommunityPost(
        student_id=student_id,
        media_url=media_url,
        media_type=media_type,
        caption=caption
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post

@router.get("/feed", response_model=List[CommunityPostResponse])
def get_community_feed(db: Session = Depends(get_db), limit: int = 20):
    """Retrieve the latest memes and reels."""
    return db.query(CommunityPost).order_by(CommunityPost.created_at.desc()).limit(limit).all()

@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    """Increment the like count for a post."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.likes_count += 1
    db.commit()
    return {"message": "Post liked", "likes": post.likes_count}
