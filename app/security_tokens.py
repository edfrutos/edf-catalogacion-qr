from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from app.models import User

def verify_reset_token(token):
    """Valida un token de restablecimiento de contraseña. Usa PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS como TTL."""
    s = Serializer(current_app.config['SECRET_KEY'])
    max_age = current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS', 1800)
    try:
        user_id = s.loads(token, max_age=max_age)['user_id']
    except Exception:
        return None
    return User.objects(id=user_id).first()
