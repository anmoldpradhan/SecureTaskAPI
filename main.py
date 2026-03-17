# SecureTaskAPI - Production REST API in AWS
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.database import get_engine
from app.routers import auth, tasks, users

limiter = Limiter(key_func=get_remote_address)

# Create tables
try:
    engine = get_engine()
# Database tables managed by Alembic migrations
# Run: alembic upgrade head
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