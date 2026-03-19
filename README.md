# EDF Catalogación QR

Proyecto para catalogar objetos situados en diferentes tipos de contenedores y ser identificables por el QR generado al crear el registro.

## Tecnologías

- **Backend:** Flask, MongoEngine (MongoDB)
- **Autenticación:** Usuario/contraseña + OAuth (Google, GitHub) vía Better-Auth

## Inicio rápido

```bash
pip install -r requirements.txt
cp .env.example .env   # Editar con tus credenciales
honcho start -e .env -f Procfile.app
```

Accede a `http://localhost:5020`. Ver `GEMINI.md` para más detalles.
