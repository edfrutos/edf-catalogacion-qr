import os
import sys

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import User
# from mongoengine import connect # No es necesario conectar explícitamente

def add_missing_address_field():
    """
    Añade un campo 'address' vacío a los usuarios que no lo tengan.
    Usa el contexto de la aplicación Flask para la configuración de la BD.
    """
    app = create_app()
    with app.app_context():
        print("Buscando usuarios sin campo 'address'...")
        users_to_update = User.objects(address__exists=False) # Más eficiente que hasattr

        count = 0
        for user in users_to_update:
            user.address = ''  # Valor predeterminado
            user.save()
            count += 1
            print(f"Campo 'address' añadido para el usuario '{user.username}' (ID: {user.id})")

        if count > 0:
            print(f"\nSe actualizó el campo 'address' para {count} usuario(s).")
        else:
            print("\nNo se encontraron usuarios que necesitaran actualización del campo 'address'.")

if __name__ == '__main__':
    print("Iniciando script para actualizar campo 'address' en documentos User...")
    add_missing_address_field()
    print("Script finalizado.")