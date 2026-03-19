#!/usr/bin/env python3
"""
Script para verificar si un usuario existe y la contraseña es correcta.
Uso: python check_user.py [usuario_o_email] [contraseña]
"""

import os
import sys

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from app import create_app
    from app.models import User

    identifier = sys.argv[1] if len(sys.argv) > 1 else input("Usuario o email: ").strip()
    password = sys.argv[2] if len(sys.argv) > 2 else input("Contraseña: ").strip()

    if not identifier or not password:
        print("Debes indicar usuario/email y contraseña.")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        user = User.objects(email=identifier).first() or User.objects(username=identifier).first()
        if not user:
            print(f"❌ Usuario no encontrado: '{identifier}'")
            print("Usuarios en BD:", [u.username for u in User.objects()])
            sys.exit(1)
        if user.check_password(password):
            print(f"✅ OK: {user.username} ({user.email})")
        else:
            print(f"❌ Contraseña incorrecta para '{user.username}'")

if __name__ == "__main__":
    main()
