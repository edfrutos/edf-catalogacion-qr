from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_mongoengine import MongoEngine
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

def create_app(config_class=Config):
    app = Flask(__name__)
    # Cargar configuración desde Config object. Esto incluye MONGODB_SETTINGS.
    app.config.from_object(config_class)

    # Solo aplicar configuración TLS si hay un host definido y no estamos en modo mock/testing con mongomock
    if app.config.get('MONGODB_SETTINGS') and app.config['MONGODB_SETTINGS'].get('host'):
        if not app.config['MONGODB_SETTINGS'].get('is_mock'):
            app.config['MONGODB_SETTINGS'].update({
                'tls': True,
                'tlsAllowInvalidCertificates': False,
                'ssl_cert_reqs': ssl.CERT_REQUIRED,
            })

    # Asegurar otras configuraciones que podrían no estar en Config object
    app.config.setdefault('SECRET_KEY', os.getenv('SECRET_KEY', 'a_very_secure_default_secret_key_CHANGE_ME'))
    app.config.setdefault('MAIL_SERVER', os.getenv('MAIL_SERVER', 'smtp.example.com'))
    app.config.setdefault('MAIL_PORT', int(os.getenv('MAIL_PORT', 587)))
    app.config.setdefault('MAIL_USE_TLS', os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'])
    app.config.setdefault('MAIL_USERNAME', os.getenv('EMAIL_USER'))
    app.config.setdefault('MAIL_PASSWORD', os.getenv('EMAIL_PASS'))
    app.config.setdefault('WTF_CSRF_ENABLED', True)


    db.init_app(app) # MongoEngine se inicializa aquí usando app.config['MONGODB_SETTINGS']
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Las llamadas explícitas a disconnect() y connect() han sido eliminadas.
    # db.init_app(app) maneja la conexión.

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.admin.routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app