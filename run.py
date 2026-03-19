"""
Módulo de entrada principal para la aplicación Flask.

Este script inicializa la aplicación y lanza el servidor de desarrollo.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.getenv('FLASK_RUN_PORT', 5020))
    app.run(debug=True, port=port)
