"""
Script para la creación interactiva de un usuario administrador.
"""

import os
import sys
import getpass


def do_create_admin():
    """
    Crea un usuario administrador solicitando datos por consola.
    """
    # Ajuste de ruta local para permitir ejecución directa
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    from app import create_app
    from app.models import User

    print("\n--- Configuración de Usuario Administrador ---")
    
    # Solicitar Username
    env_user = os.getenv('ADMIN_USERNAME', 'admin')
    admin_username = input(f"Introduce nombre de usuario [{env_user}]: ").strip() or env_user
    
    # Solicitar Email
    env_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_email = input(f"Introduce email [{env_email}]: ").strip() or env_email
    
    # Solicitar Password de forma segura
    admin_password = getpass.getpass("Introduce contraseña: ").strip()
    if not admin_password:
        admin_password = os.getenv('ADMIN_PASSWORD', 'changeme!')
        if admin_password == 'changeme!':
            print("AVISO: Usando contraseña por defecto 'changeme!'.")

    app = create_app()
    with app.app_context():
        # Verificación de duplicados mejorada
        if User.objects(username=admin_username).first():
            print(f"\nERROR: El nombre de usuario '{admin_username}' ya existe.")
            return
        
        if User.objects(email=admin_email).first():
            print(f"\nERROR: El email '{admin_email}' ya está registrado.")
            return

        print(f"\nCreando admin '{admin_username}'...")
        user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True
        )
        user.set_password(admin_password)
        try:
            user.save()
            print(f"¡ÉXITO! Usuario '{admin_username}' creado correctamente.")
        except Exception as e:
            print(f"\nERROR inesperado al guardar: {e}")


if __name__ == '__main__':
    try:
        do_create_admin()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)
