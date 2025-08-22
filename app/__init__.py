from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Inicializar extensiones
    db.init_app(app)

    # Ruta básica para verificar que funciona
    @app.route('/')
    def home():
        return {'message': 'Task Manager API', 'status': 'running'}

    return app
