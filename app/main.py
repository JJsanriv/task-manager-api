from fastapi import FastAPI
from app.routers import tasks

app = FastAPI(
    title="Task Manager API",
    description="A simple REST API for managing tasks",
    version="1.0.0"
)

app.include_router(tasks.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Task Manager API"}
