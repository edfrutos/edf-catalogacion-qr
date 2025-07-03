import os
import sys

# Añadir el directorio raíz del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import create_app
from app.models import Container

def remove_date_posted_from_containers():
    """
    Elimina el campo 'date_posted' de todos los documentos Container.
    """
    app = create_app()
    with app.app_context():
        print("Buscando contenedores con el campo 'date_posted'...")
        # Usar __exists=True es más eficiente para encontrar documentos con el campo
        containers_with_field = Container.objects(date_posted__exists=True)

        count = 0
        for container in containers_with_field:
            # El método 'unset' elimina el campo del documento.
            container.unset('date_posted')
            # No es necesario llamar a save() después de unset si se usa update.
            # Pero si se itera sobre objetos, save() es correcto.
            # Para mayor eficiencia en muchos documentos, se podría hacer un update:
            # Container.objects(id=container.id).update_one(unset__date_posted=1)
            # pero el bucle es más claro para pocos cambios.
            container.save()
            count += 1
            print(f"Campo 'date_posted' eliminado del contenedor '{container.name}' (ID: {container.id})")

        if count > 0:
            print(f"\nSe eliminó el campo 'date_posted' de {count} contenedor(es).")
        else:
            print("\nNo se encontraron contenedores con el campo 'date_posted'.")

if __name__ == '__main__':
    print("Iniciando script para limpiar campo 'date_posted' de Contenedores...")
    remove_date_posted_from_containers()
    print("Script finalizado.")