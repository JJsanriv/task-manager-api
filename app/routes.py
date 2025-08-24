from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app import db
from app.models import Task

# Crear namespace para organizar rutas
tasks_ns = Namespace('tasks', description='Operaciones con tareas')

# Modelo para documentación automática
task_model = tasks_ns.model('Task', {
    'id': fields.Integer(description='ID de la tarea'),
    'title': fields.String(required=True, description='Título de la tarea'),
    'description': fields.String(description='Descripción de la tarea'),
    'completed': fields.Boolean(description='Estado de completado'),
    'created_at': fields.String(description='Fecha de creación'),
    'updated_at': fields.String(description='Fecha de actualización')
})

task_input = tasks_ns.model('TaskInput', {
    'title': fields.String(required=True, description='Título de la tarea'),
    'description': fields.String(description='Descripción de la tarea'),
    'completed': fields.Boolean(description='Estado de completado')
})


@tasks_ns.route('/tasks')
class TaskList(Resource):
    @tasks_ns.marshal_list_with(task_model)
    def get(self):
        """Obtener todas las tareas"""
        tasks = Task.query.all()
        return [task.to_dict() for task in tasks]

    @tasks_ns.expect(task_input)
    @tasks_ns.marshal_with(task_model, code=201)
    def post(self):
        """Crear una nueva tarea"""
        data = request.json

        # Validación básica
        if not data or not data.get('title'):
            tasks_ns.abort(400, 'Title is required')

        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )

        try:
            db.session.add(task)
            db.session.commit()
            return task.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            tasks_ns.abort(500, f'Error creating task: {str(e)}')


@tasks_ns.route('/tasks/<int:task_id>')
class TaskResource(Resource):
    @tasks_ns.marshal_with(task_model)
    def get(self, task_id):
        """Obtener una tarea específica"""
        task = Task.query.get_or_404(task_id)
        return task.to_dict()

    @tasks_ns.expect(task_input)
    @tasks_ns.marshal_with(task_model)
    def put(self, task_id):
        """Actualizar una tarea"""
        task = Task.query.get_or_404(task_id)
        data = request.json

        if not data:
            tasks_ns.abort(400, 'No data provided')

        # Actualizar campos
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)

        try:
            db.session.commit()
            return task.to_dict()
        except Exception as e:
            db.session.rollback()
            tasks_ns.abort(500, f'Error updating task: {str(e)}')

    def delete(self, task_id):
        """Eliminar una tarea"""
        task = Task.query.get_or_404(task_id)

        try:
            db.session.delete(task)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            tasks_ns.abort(500, f'Error deleting task: {str(e)}')
