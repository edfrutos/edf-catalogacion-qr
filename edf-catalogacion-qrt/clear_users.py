import os
import sys
import time

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import User
# from mongoengine import disconnect # No es necesario

def clear_all_users():
    """
    Elimina TODOS los usuarios de la base de datos después de una confirmación
    y una cuenta atrás. Excluye al usuario 'admin' por defecto si existe.
    """
    app = create_app()
    with app.app_context():
        admin_username_to_keep = os.getenv('ADMIN_USERNAME', 'admin') # Para no borrar el admin por defecto

        print(f"ADVERTENCIA: Esta acción eliminará TODOS los usuarios de la base de datos, EXCEPTO '{admin_username_to_keep}' si existe.")
        confirm = input("¿Estás seguro de que quieres continuar? (escribe 'si' para confirmar): ")

        if confirm.lower() == 'si':
            print("Eliminación comenzará en 5 segundos. Presiona Ctrl+C para cancelar.")
            try:
                for i in range(5, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)

                print(f"Eliminando todos los usuarios excepto '{admin_username_to_keep}'...")
                # No eliminar el usuario admin por defecto
                users_to_delete = User.objects(username__ne=admin_username_to_keep)
                deleted_count = users_to_delete.delete()

                admin_user = User.objects(username=admin_username_to_keep).first()
                if admin_user:
                    print(f"El usuario administrador '{admin_username_to_keep}' no ha sido eliminado.")
                else:
                    print(f"No se encontró el usuario administrador '{admin_username_to_keep}'.")

                print(f"Se han eliminado {deleted_count} usuarios de la base de datos.")
            except KeyboardInterrupt:
                print("\nEliminación cancelada por el usuario.")
        else:
            print("Eliminación cancelada. No se realizaron cambios.")

if __name__ == '__main__':
    clear_all_users()
    print("Script para limpiar usuarios finalizado.")