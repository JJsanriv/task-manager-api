import pytest
from datetime import datetime
from app import create_app, db
from app.models import Task


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def app_context(app):
    """Contexto de aplicación para pruebas"""
    with app.app_context():
        yield app


def test_task_creation(app_context):
    """Probar creación de tarea"""
    task = Task(title="Test Task", description="Test Description")
    db.session.add(task)
    db.session.commit()

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)


def test_task_to_dict(app_context):
    """Probar conversión a diccionario"""
    task = Task(title="Test Task", description="Test Description", completed=True)
    db.session.add(task)
    db.session.commit()

    task_dict = task.to_dict()

    assert task_dict['title'] == "Test Task"
    assert task_dict['description'] == "Test Description"
    assert task_dict['completed'] is True
    assert 'created_at' in task_dict
    assert 'updated_at' in task_dict
    assert 'id' in task_dict


def test_task_repr(app_context):
    """Probar representación string de tarea"""
    task = Task(title="Test Task")
    db.session.add(task)
    db.session.commit()

    assert "Test Task" in repr(task)
    assert str(task.id) in repr(task)
