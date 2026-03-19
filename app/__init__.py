from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_mongoengine import MongoEngine
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# from mongoengine import connect, disconnect # No longer needed here
from config import Config
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

db = MongoEngine()
bcrypt = Bcrypt() # bcrypt será usado por el modelo User desde esta instancia
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def create_app(config_class=Config):
    app = Flask(__name__)
    # Cargar configuración desde el objeto proporcionado (Config por defecto)
    app.config.from_object(config_class)

    # Solo aplicar configuración TLS si hay un host definido y no estamos en modo mock/testing
    if app.config.get('MONGODB_SETTINGS') and app.config['MONGODB_SETTINGS'].get('host'):
        if not app.config['MONGODB_SETTINGS'].get('is_mock'):
            allow_invalid = os.getenv('MONGO_TLS_ALLOW_INVALID_CERTS', '').lower() in ('1', 'true', 'yes')
            app.config['MONGODB_SETTINGS'].update({
                'tls': True,
                'tlsAllowInvalidCertificates': allow_invalid,
                'ssl_cert_reqs': ssl.CERT_NONE if allow_invalid else ssl.CERT_REQUIRED,
            })

    # Asegurar que SECRET_KEY tenga un valor si no viene del objeto config
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_very_secure_default_secret_key_CHANGE_ME')

    host = (app.config['MONGODB_SETTINGS'].get('host') or '')[:50]
    db_name = app.config['MONGODB_SETTINGS'].get('db', 'NO DEFINIDA')
    print(f"[DEBUG] Inicializando MongoEngine. Host: {host}... BD Target: {db_name}")
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Las llamadas explícitas a disconnect() y connect() han sido eliminadas.
    # db.init_app(app) maneja la conexión.

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.admin.routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app