#!/usr/bin/env python3
"""
Migra usuarios de la colección 'user' a 'app_users'.
Solo copia documentos que tengan el esquema de nuestra app (username, password).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from pymongo import MongoClient

def main():
    app = create_app()
    with app.app_context():
        uri = os.getenv('MONGO_URI')
        if not uri:
            print("MONGO_URI no definido")
            sys.exit(1)
        client = MongoClient(uri)
        db = client['test']
        user_coll = db['user']
        app_users = db['app_users']
        # Solo documentos con username y password (nuestro esquema)
        migrated = 0
        for doc in user_coll.find({'username': {'$exists': True}, 'password': {'$exists': True}}):
            if not app_users.find_one({'email': doc['email']}):
                app_users.insert_one(doc.copy())
                migrated += 1
                print(f"  Migrado: {doc.get('username')} ({doc.get('email')})")
        print(f"Migración completada. {migrated} usuarios copiados a app_users.")

if __name__ == '__main__':
    main()
