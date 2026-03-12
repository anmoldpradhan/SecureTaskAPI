from app.dependencies import get_current_user
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate,UserResponse
import bcrypt
from app.dependencies import get_admin_user,get_current_user
from typing import List

router=APIRouter(
    prefix="/users",
    tags=["Users"],
)

def hash_password(password:str)->str:
    return bcrypt.hashpw(password.encode('utf-8')[:72], bcrypt.gensalt()).decode('utf-8')

@router.post("/",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    existing=db.query(User).filter(User.email==user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    new_user=User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me",response_model=UserResponse)
def get_me(current_user:User=Depends(get_current_user)):
    return current_user

@router.get("/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/",response_model=List[UserResponse])
def get_all_users(
    db:Session=Depends(get_db),
    create_user:User=Depends(get_admin_user)
):
    return db.query(User).all()

@router.delete("/{user_id}")
def delete_user(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_admin_user)
):
    user=db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return None