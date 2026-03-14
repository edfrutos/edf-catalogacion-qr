import pytest
from app import create_app, db
from config import Config
from mongoengine import connect, disconnect

class TestConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/test_db',
        'is_mock': True  # Usaremos mongomock para las pruebas
    }
    WTF_CSRF_ENABLED = False  # Deshabilitar CSRF para facilitar las pruebas de formularios

@pytest.fixture(scope='session')
def app():
    # Desconectar cualquier conexión previa de MongoEngine
    disconnect()
    
    app = create_app()
    app.config.from_object(TestConfig)
    
    # MongoEngine se inicializa con MONGODB_SETTINGS en create_app() -> db.init_app(app)
    # Sin embargo, para forzar mongomock, a veces es necesario conectarlo explícitamente 
    # si db.init_app no lo hace automáticamente con el flag is_mock.
    
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    # Limpiar la base de datos antes de cada test
    with app.app_context():
        db.connection.drop_database('test_db')
        yield db
