import mongoengine as db
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("MONGO_URI")

if not DB_URI:
    print("Error: MONGO_URI no está definido en el entorno.")
    exit(1)

try:
    db.connect(host=DB_URI)
    print("Conexión exitosa a MongoDB Atlas")
except Exception as e:
    print(f"Error al conectar a MongoDB Atlas: {e}")