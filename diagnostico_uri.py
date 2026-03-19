#!/usr/bin/env python3
"""
Diagnóstico: qué MONGO_URI usa cada contexto.
Ejecutar de distintas formas para comparar:
  python diagnostico_uri.py           # Python directo (load_dotenv)
  honcho run -e .env python diagnostico_uri.py   # Honcho inyecta .env
"""
import os
import re

# Simular qué hace cada uno ANTES de cargar la app
def _mask_uri(uri):
    if not uri:
        return "(no definida)"
    # Mostrar usuario y host para identificar: mongodb+srv://USUARIO:xxx@host...
    m = re.match(r'mongodb(?:\+srv)?://([^:]+):[^@]+@([^/]+)', uri)
    if m:
        return f"mongodb+srv://{m.group(1)}:***@{m.group(2)[:30]}..."
    return uri[:50] + "..."

print("=" * 60)
print("DIAGNÓSTICO MONGO_URI")
print("=" * 60)

# 1) Estado ANTES de load_dotenv
uri_antes = os.environ.get("MONGO_URI")
print(f"\n1) ANTES de load_dotenv():")
print(f"   MONGO_URI en os.environ: {_mask_uri(uri_antes) if uri_antes else '(no existe)'}")
print(f"   Origen: {'shell/honcho (ya inyectada)' if uri_antes else 'ninguno'}")

# 2) Cargar .env como hace la app
from dotenv import load_dotenv
load_dotenv()

uri_despues = os.environ.get("MONGO_URI")
print(f"\n2) DESPUÉS de load_dotenv():")
print(f"   MONGO_URI en os.environ: {_mask_uri(uri_despues) if uri_despues else '(no existe)'}")

# 3) Lo que verá Config (vía create_app)
from config import Config
uri_config = Config.MONGODB_SETTINGS.get("host")
db_config = Config.MONGODB_SETTINGS.get("db")
print(f"\n3) Config (lo que usa Flask):")
print(f"   MONGO_URI: {_mask_uri(uri_config)}")
print(f"   MONGODB_DB: {db_config}")

# 4) Identificar usuario en URI
if uri_config:
    mu = re.search(r'mongodb(?:\+srv)?://([^:]+):', uri_config)
    user = mu.group(1) if mu else "?"
    print(f"\n4) Usuario en URI: '{user}'")
    if user == "edfrutos":
        print("   → Conexión: edfrutos (credenciales .env)")
    elif user == "edfrutos_net":
        print("   → Conexión: edfrutos_net (credenciales shell/otro .env)")
    else:
        print(f"   → Conexión: {user}")

print("\n" + "=" * 60)
print("RESUMEN:")
print("  - python script.py                  → usa MONGO_URI del SHELL (si existe)")
print("  - honcho run -e .env python ...     → honcho inyecta .env (sobrescribe)")
print("  - honcho start -e .env -f Procfile  → Flask usa .env inyectado por honcho")
print("=" * 60)
