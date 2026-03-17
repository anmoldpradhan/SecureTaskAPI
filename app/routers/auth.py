import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password, verify_token
from app.database import get_db
from app.dependencies import get_current_user, oauth2_scheme
from app.models import User
from app.redis_client import add_token_to_blacklist
from app.schemas import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
TESTING = os.getenv("TESTING", "false").lower() == "true"

def login_endpoint(request: Request, form_data, db):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role
    })
    return {"access_token": access_token, "token_type": "bearer"}

if TESTING:
    @router.post("/login", response_model=Token)
    def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
        return login_endpoint(request, form_data, db)
else:
    @router.post("/login", response_model=Token)
    @limiter.limit("5/minute")
    def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
        return login_endpoint(request, form_data, db)

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    payload = verify_token(token)
    if payload:
        import time
        exp = payload.get("exp", 0)
        remaining = int(exp - time.time())
        if remaining > 0:
            add_token_to_blacklist(token, remaining)
    return {"message": "Successfully logged out"}