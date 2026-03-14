import os
import sys
import re

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import User  # Importar el modelo User real
# bcrypt se usa a través de user.set_password() y user.check_password()

def check_and_report_passwords():
    """
    Verifica las contraseñas de los usuarios. Si una contraseña no está en formato bcrypt,
    imprime una advertencia para ese usuario. No intenta convertir automáticamente
    contraseñas debido al riesgo de corrupción si el formato original es desconocido.
    """
    app = create_app()
    with app.app_context():
        users = User.objects()

        # Regex para verificar el formato bcrypt (similar al de verificacion_programatica.py)
        # $2b$ (coste de 12) y 53 caracteres restantes (salt + hash)
        bcrypt_regex = re.compile(r'^\$2b\$[0-9]{2}\$[./A-Za-z0-9]{53}$')

        print("Iniciando verificación de formato de contraseñas...")
        updated_count = 0
        warning_count = 0

        for user in users:
            if user.password:
                if bcrypt_regex.match(user.password):
                    # print(f"Contraseña para '{user.username}' ya está en formato bcrypt.")
                    pass # No hacer nada si ya está en formato correcto
                else:
                    # Si no está en formato bcrypt, podría ser texto plano o un hash antiguo.
                    # No intentaremos convertirla automáticamente para evitar corrupción.
                    print(f"ADVERTENCIA: La contraseña para el usuario '{user.username}' (ID: {user.id}) no está en formato bcrypt.")
                    print(f"   Hash actual (primeros 10 chars): {user.password[:10]}...")
                    print(f"   Este usuario podría no poder iniciar sesión o su contraseña podría ser insegura.")
                    print(f"   Se recomienda un reseteo de contraseña para este usuario o una migración manual si se conoce el formato original.")
                    warning_count += 1
            else:
                print(f"ADVERTENCIA: El usuario '{user.username}' (ID: {user.id}) no tiene contraseña establecida.")
                warning_count += 1

        if warning_count > 0:
            print(f"\nSe encontraron {warning_count} usuarios con contraseñas que no están en formato bcrypt o sin contraseña.")
            print("Estos usuarios requieren atención manual (reseteo de contraseña o migración cuidadosa).")
        else:
            print("\nTodas las contraseñas de los usuarios (que tienen una) parecen estar en formato bcrypt.")

        # La lógica de actualización automática ha sido eliminada por seguridad.
        # Si se quisiera re-hashear contraseñas que se sabe son texto plano:
        # if not bcrypt_regex.match(user.password):
        #     print(f"Intentando re-hashear la contraseña para {user.username} asumiendo que es texto plano.")
        #     try:
        #         user.set_password(user.password) # Asume que user.password es texto plano
        #         user.save()
        #         print(f"Contraseña para {user.username} re-hasheada a bcrypt.")
        #         updated_count += 1
        #     except Exception as e:
        #         print(f"Error re-hasheando contraseña para {user.username}: {e}")


if __name__ == "__main__":
    check_and_report_passwords()
    print("Script de verificación de contraseñas finalizado.")