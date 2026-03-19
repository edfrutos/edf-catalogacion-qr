"""Script para resetear contraseña de un usuario. Solo en desarrollo."""
import os
import sys
import getpass

from app import create_app
from app.models import User

# No ejecutar en producción
if os.getenv("FLASK_ENV") == "production" or os.getenv("ENV") == "production":
    print("ERROR: Este script no debe ejecutarse en producción.")
    sys.exit(1)

app = create_app()
with app.app_context():
    password = os.getenv("RESET_USER_PASSWORD")
    if not password:
        password = getpass.getpass("Nueva contraseña para testuser: ")
    if not password:
        print("ERROR: La contraseña no puede estar vacía.")
        sys.exit(1)

    user = User.objects(username="testuser").first()
    if user:
        user.set_password(password)
        user.save()
        print("USUARIO 'testuser' ACTUALIZADO.")
    else:
        user = User(username="testuser", email="test@example.com")
        user.set_password(password)
        user.save()
        print("USUARIO 'testuser' CREADO.")
