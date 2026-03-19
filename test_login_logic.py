from app import create_app, bcrypt
from app.models import User

app = create_app()
with app.app_context():
    username = "edefrutos"
    password_to_check = "34Maf15si"

    user = User.objects(username=username).first()
    if not user:
        print(f"ERROR: Usuario {username} no encontrado en la base de datos.")
    else:
        print(f"Usuario encontrado: {user.username}")
        print(f"Hash en BD: {user.password}")

        # Prueba directa con bcrypt
        is_correct = bcrypt.check_password_hash(user.password, password_to_check)
        print(f"¿Contraseña '34Maf15si' es correcta? {is_correct}")

        # Prueba con el método del modelo
        is_correct_method = user.check_password(password_to_check)
        print(f"¿Método user.check_password() funciona? {is_correct_method}")
