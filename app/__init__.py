from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.errors import register_error_handlers
from datetime import  timedelta
from flasgger import Swagger  # Agrega esto arriba con tus imports

db = SQLAlchemy()          # Creamos una instancia global de la base de datos (SQLAlchemy)
migrate = Migrate()        # Creamos instancia para migraciones con Alembic/Flask-Migrate
jwt = JWTManager()         # Creamos instancia para manejo de JWT (tokens de seguridad)

def create_app():
    app = Flask(__name__)  # Creamos la app Flask

    # Configuraciones básicas
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'  # Ruta a la base de datos SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Desactivar para no usar tracking (optimiza)
    app.config['JWT_SECRET_KEY'] = 'El que siembra vientos cosecha tempestades'  # Clave secreta para firmar tokens JWT

    # Duración del token (60 minutos)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)

    # Inicializamos las extensiones pasándoles la app y otros parámetros si aplica
    db.init_app(app)        # Inicializa la base de datos con la app creada
    migrate.init_app(app, db)  # Inicializa migraciones pasándole la app y el objeto db
    jwt.init_app(app)       # Inicializa JWT para manejo de autenticación por token

    # Inicializa Swagger (aquí lo agregas)
    Swagger(app)

    # Aquí abrimos el contexto de la app para registrar rutas y otras cosas
    with app.app_context():
        from .routes import main_bp   # Importamos el blueprint de rutas
        app.register_blueprint(main_bp)  # Registramos el blueprint para que Flask lo reconozca
        # db.create_all()  # Comentado porque usas migraciones, no creas tablas directamente aquí

    # Registramos los manejadores de error personalizados (por ejemplo 404, 500, etc)
    register_error_handlers(app)

    # Finalmente retornamos la app creada y configurada
    return app
