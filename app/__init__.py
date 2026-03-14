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

def create_app():
    app = Flask(__name__)
    # Cargar configuración desde Config object. Esto incluye MONGODB_SETTINGS.
    app.config.from_object(Config)

    # Sobrescribir o asegurar configuraciones específicas si es necesario,
    # pero MONGODB_SETTINGS de Config debería ser la fuente principal.
    # Si MONGO_URI no está en .env, Config.MONGO_URI será None,
    # y Config.MONGODB_SETTINGS['host'] usará el valor por defecto hardcodeado allí.
    # Para mayor claridad, podríamos re-evaluar MONGODB_SETTINGS aquí si fuera necesario
    # asegurar que MONGO_URI de os.getenv tiene precedencia si Config no lo manejara bien.
    # Por ahora, asumimos que Config.MONGODB_SETTINGS es suficiente.

    # Actualizar la configuración de MONGODB_SETTINGS para TLS seguro
    # Esto sobreescribirá/añadirá a lo que venga de Config.
    # Es importante que 'host' ya esté definido en app.config['MONGODB_SETTINGS'] desde Config.
    # Config.py asegura que MONGODB_SETTINGS y MONGODB_SETTINGS['host'] siempre existan.
    app.config['MONGODB_SETTINGS'].update({
        'tls': True, # Asumimos que TLS siempre se desea para MongoDB Atlas
        'tlsAllowInvalidCertificates': False,  # CORREGIDO
        'ssl_cert_reqs': ssl.CERT_REQUIRED, # CORREGIDO
        # El nombre 'db' puede estar en la MONGO_URI o especificarse aquí.
        # Si está en la URI, esta especificación es redundante o puede causar conflictos
        # dependiendo del driver. Por ahora, se deja que la URI lo maneje o que
        # Config.MONGODB_SETTINGS ya lo tenga si es necesario separarlo.
        # 'db': 'app-qr-catalogacion',
    })

    # Asegurar otras configuraciones que podrían no estar en Config object
    # o para darles un valor por defecto si no están en .env Y no están en Config.
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