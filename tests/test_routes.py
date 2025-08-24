import pytest
import json
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
def client(app):
    """Cliente de prueba"""
    return app.test_client()


@pytest.fixture
def sample_task(app):
    """Crear tarea de muestra para pruebas"""
    with app.app_context():
        task = Task(title="Sample Task", description="Sample Description")
        db.session.add(task)
        db.session.commit()
        return task.id


def test_get_empty_tasks(client):
    """Probar obtener lista vacía de tareas"""
    response = client.get('/api/v1/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []


def test_create_task_success(client):
    """Probar creación exitosa de tarea"""
    response = client.post('/api/v1/tasks',
                           json={'title': 'New Task', 'description': 'New Description'})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'New Task'
    assert data['description'] == 'New Description'
    assert data['completed'] is False
    assert 'id' in data


def test_create_task_missing_title(client):
    """Probar creación de tarea sin título"""
    response = client.post('/api/v1/tasks', json={'description': 'No title'})
    assert response.status_code == 400


def test_create_task_empty_body(client):
    """Probar creación de tarea con body vacío"""
    response = client.post('/api/v1/tasks', json={})
    assert response.status_code == 400


def test_get_all_tasks(client, sample_task):
    """Probar obtener todas las tareas"""
    response = client.get('/api/v1/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Sample Task'


def test_get_task_by_id(client, sample_task):
    """Probar obtener tarea por ID"""
    response = client.get(f'/api/v1/tasks/{sample_task}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Sample Task'
    assert data['id'] == sample_task


def test_get_task_not_found(client):
    """Probar obtener tarea inexistente"""
    response = client.get('/api/v1/tasks/999')
    assert response.status_code == 404


def test_update_task_success(client, sample_task):
    """Probar actualización exitosa de tarea"""
    response = client.put(f'/api/v1/tasks/{sample_task}',
                          json={'title': 'Updated Task', 'completed': True})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Task'
    assert data['completed'] is True


def test_update_task_not_found(client):
    """Probar actualizar tarea inexistente"""
    response = client.put('/api/v1/tasks/999',
                          json={'title': 'Updated Task'})
    assert response.status_code == 404


def test_update_task_empty_body(client, sample_task):
    """Probar actualizar tarea con body vacío"""
    response = client.put(f'/api/v1/tasks/{sample_task}', json={})
    assert response.status_code == 400


def test_delete_task_success(client, sample_task):
    """Probar eliminación exitosa de tarea"""
    response = client.delete(f'/api/v1/tasks/{sample_task}')
    assert response.status_code == 204

    # Verificar que se eliminó
    response = client.get(f'/api/v1/tasks/{sample_task}')
    assert response.status_code == 404


def test_delete_task_not_found(client):
    """Probar eliminar tarea inexistente"""
    response = client.delete('/api/v1/tasks/999')
    assert response.status_code == 404


def test_api_workflow(client):
    """Probar flujo completo de la API"""
    # Crear tarea
    response = client.post('/api/v1/tasks',
                           json={'title': 'Workflow Test', 'description': 'Testing complete workflow'})
    assert response.status_code == 201
    task_id = json.loads(response.data)['id']

    # Obtener tarea
    response = client.get(f'/api/v1/tasks/{task_id}')
    assert response.status_code == 200

    # Actualizar tarea
    response = client.put(f'/api/v1/tasks/{task_id}',
                          json={'completed': True})
    assert response.status_code == 200

    # Verificar actualización
    response = client.get(f'/api/v1/tasks/{task_id}')
    data = json.loads(response.data)
    assert data['completed'] is True

    # Eliminar tarea
    response = client.delete(f'/api/v1/tasks/{task_id}')
    assert response.status_code == 204
