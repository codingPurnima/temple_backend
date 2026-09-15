from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import or_, func

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.lyrics import Lyrics
from app.models.roles import UserRole
from app.models.user import User
from app.schemas.lyrics import LyricsSchema, LyricsOut, LyricsUpdate
from app.services.role_service import require_role

router = APIRouter(tags=["lyrics"])

@router.post("/add", response_model=LyricsOut, status_code=201)
def create_lyrics(
    data: LyricsSchema,
    db: Session = Depends(get_db),
    user= Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    try:
        lyric = Lyrics(**data.model_dump())

        db.add(lyric)
        db.commit()
        db.refresh(lyric)

        return lyric

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create lyric"
        )

@router.get("/get", response_model=list[LyricsOut])
def get_lyrics(
    search: str | None = None,
    skip: int=0,
    limit: int= Query(default=100, le=500),
    db: Session= Depends(get_db)
):
    query= db.query(Lyrics)

    if search:
        search_item= f"%{search.lower()}%"
        query= query.filter(
            or_(
                func.lower(Lyrics.title).like(search_item),
                func.lower(Lyrics.author).like(search_item)
            )
            
        )
    query= query.order_by(Lyrics.id.desc())

    lyrics= query.offset(skip).limit(limit).all()
    return lyrics

@router.get("/by-id/{lyric_id}", response_model=LyricsOut)
def get_lyric(
    lyric_id: int,
    db: Session= Depends(get_db)
):
    lyric= db.get(Lyrics, lyric_id)

    if not lyric:
        raise HTTPException(status_code=404, detail="Lyrics not found")
    return lyric

@router.delete("/{lyric_id}")
def delete_lyric(
    lyric_id: int, 
    user: User= Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    db: Session= Depends(get_db)
):
    
    lyric= db.get(Lyrics, lyric_id)

    if not lyric:
        raise HTTPException(status_code=404, detail="Lyric not found")
    
    try:
        db.delete(lyric)
        db.commit()

        return {
            "message": "Lyric deleted successfully"
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete lyric"
        )


@router.patch("/{lyric_id}", response_model=LyricsOut)
def update_lyric(
    lyric_id: int, 
    payload: LyricsUpdate,
    user: User= Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    db: Session= Depends(get_db)
):
    
    lyric = db.get(Lyrics, lyric_id)

    if not lyric:
        raise HTTPException(status_code=404, detail="Lyric not found")
    
    update_data= payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    try:
        for key, value in update_data.items():
            setattr(lyric, key, value)

        db.commit()
        db.refresh(lyric)

        return lyric
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update lyric")