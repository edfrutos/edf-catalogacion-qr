# GEMINI.md - EDF Catalogación QR

## Project Overview

**EDF Catalogación QR** is a web application designed to catalog containers and objects, generating unique QR codes for easy identification. It is built using **Python/Flask** and **MongoDB** (via MongoEngine).

### Key Technologies

- **Backend:** Flask 2.1.3 (Downgraded for compatibility)
- **Database:** MongoDB Atlas (managed via `flask-mongoengine` 1.0.0 and `mongoengine` 0.24.1)
- **Frontend:** Jinja2 templates, Vanilla CSS, and `qrcode` for QR generation.
- **Authentication:** `Flask-Login`, `Flask-Bcrypt`, y **Better-Auth** (OAuth con Google/GitHub). Login dual: usuario/contraseña (colección `user`) y OAuth.
- **Forms:** `Flask-WTF` with CSRF protection.
- **Mailing:** `Flask-Mail` (configured for Brevo SMTP).

### Workflow

- **Auxly** (MCP-based workflow): Mandatory task management and development process for AI agents. See `.antigravityrules` and `.agent/rules/`.

---

## Architecture and Structure

The project follows a modular structure using Flask Blueprints:

- `app/main`: Core functionality (home, container management, QR generation).
- `app/admin`: Admin dashboard for user and container management.
- `app/models.py`: MongoEngine documents (`User`, `Container`).
- `app/forms.py`: WTForms definitions.
- `app/static/`: CSS, profile pictures, and generated QR codes.
- `app/templates/`: Jinja2 templates organized by module.

---

## Development and Operations

### Building and Running

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**

   Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Required variables:
   - `SECRET_KEY`: Long, random string. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`.
   - `MONGO_URI`: MongoDB Atlas connection string.
   - `MONGODB_DB`: Base de datos (ej. `test`). Opcional si la URI incluye el nombre.
   - `MONGO_TLS_ALLOW_INVALID_CERTS`: `true` en desarrollo (macOS) si falla la verificación SSL.
   - `EMAIL_USER` / `EMAIL_PASS`: Brevo SMTP credentials (login and password for smtp-relay.brevo.com).
   - `BETTER_AUTH_URL`: URL del servidor auth (ej. `http://localhost:3000`).

3. **Run in Development:**

   **Opción A – Todo junto (recomendado):**
   ```bash
   honcho start -e .env -f Procfile.app
   ```
   Arranca Flask (5020) y auth (3000). Honcho carga `.env` automáticamente.

   **Opción B – Por separado:**
   ```bash
   python run.py          # Flask en 5020
   node auth/index.js     # Auth en 3000 (otra terminal)
   ```

   Accede siempre por `http://localhost:5020` (no 0.0.0.0) para que las cookies de sesión funcionen.

4. **Run in Production:**

   Simple invocation:

   ```bash
   gunicorn run:app
   ```

   Recommended options: `-w` (workers), `-b` (bind), `--timeout` for long-running requests. Ensure `gunicorn` is in `requirements.txt` (it is). Example:

   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 run:app
   ```

### Testing

- Manual test scripts are available in the root:
  - `test_connection.py`: Verify MongoDB connectivity.
  - `test_mail.py`: Verify email configuration.
  - `check_password_formats.py` / `update_passwords.py`: Utility scripts for database maintenance.

---

## Development Conventions & Rules

### 🚨 AUXLY MANDATORY RULES

This project follows **Auxly Project Rules** (see `.antigravityrules` and `.agent/rules/`). Compliance is **non-negotiable** for AI agents:

1. **ALWAYS USE AUXLY MCP TOOLS:** Never bypass tools for creating tasks, research, logging changes, or asking questions.
2. **EXTREME TOKEN OPTIMIZATION:**
   - Max 50 words per response (excluding code).
   - No introductions, summaries, or filler phrases.
   - Execute immediately without asking for confirmation if the task is clear.
3. **MANDATORY WORKFLOW:**
   - Check existing tasks -> Get task details -> Add dual research -> Start work (flag `aiWorkingOn: true`) -> Log file changes -> Request approval.
4. **FILE LOGGING:** Use `auxly_log_change` immediately after every file modification.

### Code Style

- **Python:** PEP 8 compliance. Use `flask-mongoengine` for DB interactions.
- **Security:** Use `set_password` and `check_password` methods in the `User` model. Never log secrets.
- **Login:** Usuario/contraseña en colección `user` (bcrypt, scrypt, pbkdf2). OAuth vía Better-Auth. Script `diagnostico_uri.py` para depurar conexión MongoDB.
- **Templates:** Use `layout.html` or `base.html` as the base for all views.
- **QR Codes:** Saved in `app/static/qr_codes/` using slugified container names.

---

## Key Files

- `run.py`: Application entry point.
- `config.py`: Configuration management with `dotenv`.
- `app/__init__.py`: App factory and extension initialization.
- `app/models.py`: Data models.
- `app/routes.py`: Main application logic.
- `app/admin/routes.py`: Admin-specific logic.
- `.antigravityrules`: Critical Auxly enforcement rules.
