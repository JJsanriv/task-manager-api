from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Inicializar extensiones
    db.init_app(app)

    # Configurar API con documentación automática
    api = Api(app,
              title='Task Manager API',
              version='1.0',
              description='Una API REST para gestión de tareas con documentación automática')

    # Importar modelos
    from app.models import Task

    # Registrar rutas
    from app.routes import tasks_ns
    api.add_namespace(tasks_ns, path='/api/v1')

    # Crear tablas
    with app.app_context():
        db.create_all()

    return app
