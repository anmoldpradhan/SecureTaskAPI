from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import Token
from app.auth import verify_password,create_access_tokens

router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login",response_model=Token)
def login(
    form_data:OAuth2PasswordRequestForm=Depends(),
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(User.email==form_data.username).first()

    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate":"Bearer"}
        )
    
    access_token=create_access_tokens(data={
        "sub":str(user.id),
        "role":user.role
    })

    return {"access_token":access_token,"token_type":"bearer"}