from fastapi import APIRouter,HTTPException,Depends,status,Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import Token
from app.auth import verify_password,create_access_tokens,verify_token
from app.redis_client import add_token_to_blacklist
from app.dependencies import get_current_user,oauth2_scheme
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login",response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
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

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    payload = verify_token(token)
    if payload:
        # Calculate remaining token lifetime
        import time
        exp = payload.get("exp", 0)
        remaining = int(exp - time.time())
        if remaining > 0:
            add_token_to_blacklist(token, remaining)

    return {"message": "Successfully logged out"}