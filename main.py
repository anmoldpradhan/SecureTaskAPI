from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import Base, get_engine
from app import models
from app.routers import users, auth, tasks

limiter = Limiter(key_func=get_remote_address)

# Create tables
try:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database init skipped: {e}")

app = FastAPI(
    title="SecureTaskAPI",
    description="A production REST API with auth and RBAC",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "SecureTaskAPI is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}