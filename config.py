import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY')
    # TTL de tokens de restablecimiento de contraseña (segundos).
    # Usado en generación y validación. Default: 1800 (30 min).
    PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS = int(
        os.getenv('PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS', '1800')
    )
    
    # MongoDB Atlas
    MONGO_URI = os.getenv('MONGO_URI')
    MONGODB_SETTINGS = {
        'host': MONGO_URI
    }
    
    # Configuración de Correo (Flask-Mail)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp-relay.brevo.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Otros correos
    CONTACT_MAIL_RECIPIENT = os.getenv('CONTACT_MAIL_RECIPIENT')

    # WTF Forms
    WTF_CSRF_ENABLED = True

    # AWS S3 (Para futura implementación)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    USE_S3 = os.getenv('USE_S3', 'False').lower() in ['true', '1', 't']
