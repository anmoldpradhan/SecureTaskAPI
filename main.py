from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import users,auth,tasks
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter,_rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address)

models.Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="Secure Task API",
    description="A simple API for managing tasks with authentication",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)
@app.get("/")
def root():
    return {"message": "Welcome to the Secure Task API!"}

@app.get("/health")
def health_check():
    return {"status":"healthy"}

