import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Task Manager API"}

def test_create_task(client):
    response = client.post(
        "/api/v1/tasks/",
        json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] == False

def test_get_tasks(client):
    # Create a task first
    client.post("/api/v1/tasks/", json={"title": "Test Task"})
    
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"

def test_get_task_by_id(client):
    # Create a task first
    create_response = client.post("/api/v1/tasks/", json={"title": "Test Task"})
    task_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_update_task(client):
    # Create a task first
    create_response = client.post("/api/v1/tasks/", json={"title": "Original Title"})
    task_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"

def test_delete_task(client):
    # Create a task first
    create_response = client.post("/api/v1/tasks/", json={"title": "To Delete"})
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}
    
    # Verify task is deleted
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404