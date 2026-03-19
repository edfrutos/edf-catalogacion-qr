import os
import re
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    
    # Base de datos: usa MONGODB_DB del .env o la que venga en MONGO_URI
    _db = os.getenv('MONGODB_DB')
    if not _db and MONGO_URI:
        # Extraer db de la URI si existe (mongodb+srv://.../nombre_db?params)
        m = re.search(r'mongodb(?:\+srv)?://[^/]+/([^?]+)', MONGO_URI)
        _db = m.group(1) if m else 'test'
    MONGODB_SETTINGS = {
        'host': MONGO_URI,
        'db': _db or 'test',
        'connect': False,
    }
    
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    CONTACT_MAIL_RECIPIENT = os.getenv('CONTACT_MAIL_RECIPIENT')
    
    WTF_CSRF_ENABLED = True
    PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS = 1800
    BETTER_AUTH_URL = os.getenv('BETTER_AUTH_URL', 'http://localhost:3000')
    # Sesión: cookies en localhost
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
