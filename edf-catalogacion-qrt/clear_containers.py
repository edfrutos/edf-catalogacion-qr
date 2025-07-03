import os
import sys
import time

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import Container
# from mongoengine import disconnect # No es necesario, create_app maneja la conexión

def clear_all_containers():
    """
    Elimina TODOS los contenedores de la base de datos después de una confirmación
    y una cuenta atrás.
    """
    app = create_app()
    with app.app_context():
        print("ADVERTENCIA: Esta acción eliminará TODOS los contenedores de la base de datos.")
        confirm = input("¿Estás seguro de que quieres continuar? (escribe 'si' para confirmar): ")

        if confirm.lower() == 'si':
            print("Eliminación comenzará en 5 segundos. Presiona Ctrl+C para cancelar.")
            try:
                for i in range(5, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)

                print("Eliminando todos los contenedores...")
                deleted_count = Container.objects.delete()
                print(f"Se han eliminado {deleted_count} contenedores de la base de datos.")
            except KeyboardInterrupt:
                print("\nEliminación cancelada por el usuario.")
        else:
            print("Eliminación cancelada. No se realizaron cambios.")

if __name__ == '__main__':
    clear_all_containers()
    print("Script para limpiar contenedores finalizado.")