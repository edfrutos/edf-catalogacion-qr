from app import create_app, bcrypt
from app.models import User

app = create_app()
with app.app_context():
    user = User.objects(username="testuser").first()
    if user:
        user.set_password("admin123")
        user.save()
        print("USUARIO 'testuser' ACTUALIZADO. Contraseña: admin123")
    else:
        user = User(username="testuser", email="test@example.com")
        user.set_password("admin123")
        user.save()
        print("USUARIO 'testuser' CREADO. Contraseña: admin123")
