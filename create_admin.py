import os
import sys

# Añadir el directorio raíz del proyecto al sys.path
# Esto es necesario para que el script pueda encontrar el módulo 'app'
# cuando se ejecuta directamente.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import User # Importar el modelo User real

def do_create_admin():
    """
    Crea un usuario administrador si no existe uno.
    La configuración del admin (username, email, password) se toma de
    variables de entorno o usa valores por defecto.
    """
    app = create_app()
    with app.app_context():
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        # Es CRUCIAL que esta contraseña se cambie o se gestione de forma segura.
        admin_password_default = 'changeme!' # Contraseña por defecto MUY insegura
        admin_password = os.getenv('ADMIN_PASSWORD', admin_password_default)

        existing_admin = User.objects(username=admin_username).first()

        if existing_admin:
            print(f"El usuario administrador '{admin_username}' ya existe.")
        else:
            print(f"Creando usuario administrador '{admin_username}' con email '{admin_email}'.")
            user = User(
                username=admin_username,
                email=admin_email,
                is_admin=True
            )
            user.set_password(admin_password) # Usa el método estandarizado del modelo
            user.save()
            print(f"Usuario '{admin_username}' creado exitosamente.")
            if admin_password == admin_password_default:
                print(f"ADVERTENCIA: Se ha usado la contraseña por defecto ('{admin_password_default}').")
                print("Esta contraseña es INSEGURA. Por favor, cámbiala inmediatamente después del primer inicio de sesión o configura la variable de entorno ADMIN_PASSWORD.")

if __name__ == '__main__':
    print("Iniciando script para crear usuario administrador...")
    do_create_admin()
    print("Script finalizado.")