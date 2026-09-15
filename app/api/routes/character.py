from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.services.storage_service import upload_file
from app.models.character import Character
from app.services.role_service import require_role
from app.models.roles import UserRole
from app.schemas import character

router = APIRouter(tags=["characters"])

@router.post("/add", response_model=character.CharacterOut)
def create_character(
    data: character.CharacterCreate,
    # image_url: Optional[str]= None
    db: Session = Depends(get_db),
    user= Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    # image_url = upload_file(image)

    char = Character(**data.model_dump())

    db.add(char)
    db.commit()
    db.refresh(char)

    return char

@router.get("/get", response_model=List[character.CharacterOut])
def get_characters(
    search: Optional[str]= None,
    db: Session= Depends(get_db),
    skip: int=0,
    limit: int= Query(default=10, le=50)
):
    query= db.query(Character)

    if search:
        query = query.filter(
            func.lower(Character.name).like(f"%{search.lower()}%")
        )

    characters= query.offset(skip).limit(limit).all()
    return characters

@router.get("/by-id/{character_id}", response_model=character.CharacterOut)
def get_character(
    character_id: int,
    db: Session= Depends(get_db),
):
    character= db.query(Character).filter(Character.id== character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail= "Character not found")
    return character

@router.delete("/{id}")
def delete_character(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403)

    char = db.query(Character).filter(Character.id == id).first()

    if not char:
        raise HTTPException(status_code=404)

    db.delete(char)
    db.commit()

    return {"message": "Deleted"}

@router.patch("/{id}", response_model=character.CharacterOut)
def update_character(
    id: int, 
    payload: character.CharacterUpdate, 
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ), 
    db: Session = Depends(get_db)):

    char = db.get(Character, id)

    if not char:
        raise HTTPException(status_code=404)

    update_data= payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    try:
        for key, value in update_data.items():
            setattr(char, key, value)

        db.commit()
        db.refresh(char)

        return char
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update character")