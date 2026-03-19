from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    try:
        user_count = User.objects.count()
        print(f"CONEXIÓN BD: OK")
        print(f"USUARIOS ENCONTRADOS: {user_count}")
        if user_count > 0:
            first_user = User.objects.first()
            print(f"PRIMER USUARIO: {first_user.username} ({first_user.email})")
    except Exception as e:
        print(f"ERROR DE CONEXIÓN BD: {e}")
