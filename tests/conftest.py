import pytest
from app import create_app, db
from config import Config
from mongoengine import connect, disconnect

class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret-key' # Necesaria para sesiones en tests
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/test_db',
        'is_mock': True  # Usaremos mongomock para las pruebas
    }
    WTF_CSRF_ENABLED = False  # Deshabilitar CSRF para facilitar las pruebas de formularios

@pytest.fixture(scope='session')
def app():
    # Desconectar cualquier conexión previa de MongoEngine
    disconnect()
    
    # Pasamos TestConfig directamente a create_app para que se inicialice db con ella
    app = create_app(config_class=TestConfig)
    
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
