from fastapi import FastAPI

app=FastAPI(
    title="Secure Task API",
    description="A simple API for managing tasks with authentication",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Secure Task API!"}

@app.get("/health")
def health():
    return {"status":"healthy"}