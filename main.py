from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import users,auth

models.Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="Secure Task API",
    description="A simple API for managing tasks with authentication",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Secure Task API!"}

@app.get("/health")
def health_check():
    return {"status":"healthy"}

