import os
import sys
import re

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import User
# from werkzeug.security import check_password_hash # No se usa aquí
# import mongoengine # No es necesario para disconnect()

def verify_password_formats():
    """
    Verifica el formato de las contraseñas de todos los usuarios.
    Identifica aquellas que no parecen ser un hash bcrypt estándar.
    """
    app = create_app()
    with app.app_context():
        print("Iniciando verificación de formato de contraseñas...")
        users = User.objects()

        # Regex para verificar el formato bcrypt. Ejemplo: $2b$12$saltysaltysaltysalty...hashhashhash
        # $2b$: prefijo bcrypt
        # [0-9]{2}\$: coste (ej. 12$)
        # [./A-Za-z0-9]{53}$: 22 chars para salt base64 + 31 chars para hash base64
        bcrypt_regex = re.compile(r'^\$2b\$[0-9]{2}\$[./A-Za-z0-9]{53}$')

        correct_format_count = 0
        incorrect_format_count = 0
        no_password_count = 0

        if not users:
            print("No se encontraron usuarios en la base de datos.")
            return

        for user in users:
            if user.password:
                if bcrypt_regex.match(user.password):
                    correct_format_count += 1
                    # print(f"OK: Contraseña para '{user.username}' (ID: {user.id}) tiene formato bcrypt esperado.")
                else:
                    incorrect_format_count += 1
                    print(f"ALERTA: Contraseña para '{user.username}' (ID: {user.id}) NO coincide con el formato bcrypt esperado.")
                    print(f"        Hash actual (primeros 10 caracteres): {user.password[:10]}...")
                    print(f"        Este usuario podría tener problemas para iniciar sesión o una contraseña insegura.")
            else:
                no_password_count +=1
                print(f"ALERTA: Usuario '{user.username}' (ID: {user.id}) no tiene contraseña (campo vacío).")

        print("\nResumen de verificación de contraseñas:")
        print(f"- Usuarios con formato bcrypt correcto: {correct_format_count}")
        print(f"- Usuarios con formato incorrecto o inesperado: {incorrect_format_count}")
        print(f"- Usuarios sin contraseña establecida: {no_password_count}")

        if incorrect_format_count > 0 or no_password_count > 0:
            print("\nSe recomienda revisar los usuarios con alertas.")
            print("Para aquellos con formato incorrecto, puede ser necesario un reseteo de contraseña")
            print("o una migración manual si se conoce el formato de hash original.")
        else:
            print("\nTodas las contraseñas de los usuarios parecen estar en el formato bcrypt esperado.")

if __name__ == '__main__':
    verify_password_formats()
    print("Script de verificación de formato de contraseñas finalizado.")