from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_mongoengine import MongoEngine
from mongoengine import connect, disconnect
from config import Config
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

db = MongoEngine()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['MONGODB_SETTINGS'] = {
        'db': 'app-qr-catalogacion',
        'host': os.getenv('MONGO_URI'),
        'tls': True,
        'tlsAllowInvalidCertificates': True,
        'ssl_cert_reqs': ssl.CERT_NONE
    }
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp-relay.brevo.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    app.config['WTF_CSRF_ENABLED'] = True

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    disconnect(alias='default')
    connect(
        db=app.config['MONGODB_SETTINGS']['db'],
        host=app.config['MONGODB_SETTINGS']['host'],
        tls=True,
        tlsAllowInvalidCertificates=True,
        ssl_cert_reqs=ssl.CERT_NONE
    )

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.admin.routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app