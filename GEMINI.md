# GEMINI.md - EDF Catalogación QR

## Project Overview
**EDF Catalogación QR** is a web application designed to catalog containers and objects, generating unique QR codes for easy identification. It is built using **Python/Flask** and **MongoDB** (via MongoEngine).

### Key Technologies
- **Backend:** Flask 3.0.3
- **Database:** MongoDB Atlas (managed via `flask-mongoengine` 1.0.0 and `mongoengine` 0.24.1)
- **Frontend:** Jinja2 templates, Vanilla CSS, and `qrcode` for QR generation.
- **Authentication:** `Flask-Login` and `Flask-Bcrypt`.
- **Forms:** `Flask-WTF` with CSRF protection.
- **Mailing:** `Flask-Mail` (configured for Brevo SMTP).
- **Task Management:** **Auxly** (Mandatory MCP-based workflow).

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
   pip install -r edf-catalogacion-qrt/requirements.txt
   ```
2. **Environment Configuration:**
   Create a `.env` file in `edf-catalogacion-qrt/` with:
   - `SECRET_KEY`: Flask secret key.
   - `MONGO_URI`: MongoDB connection string.
   - `EMAIL_USER` / `EMAIL_PASS`: Brevo SMTP credentials.
3. **Run in Development:**
   ```bash
   python edf-catalogacion-qrt/run.py
   ```
4. **Run in Production:**
   ```bash
   gunicorn edf-catalogacion-qrt.run:app
   ```

### Testing
- Manual test scripts are available in the root of `edf-catalogacion-qrt/`:
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
