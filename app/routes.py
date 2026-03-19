from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Blueprint,
    abort,
    current_app,
    make_response,
    send_file,
    session,
)
from urllib.parse import quote, urlparse
from pymongo import MongoClient
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash as werkzeug_check_password
from app import db, bcrypt, mail, csrf
from app.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    ContainerForm,
    RequestResetForm,
    ResetPasswordForm,
    DeleteAccountForm,
    ContactForm,
    ChangePasswordForm,
    UpdateUserForm,
    SearchContainerForm,
)
from app.models import User, Container
from app.main.utils import save_picture, save_qr_image, slugify
from flask_mail import Message
from mongoengine.queryset.visitor import Q
import os

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html", title="Inicio")


@main.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html", title="Bienvenido")


def _check_password_any(doc, password):
    """Verifica contraseña: bcrypt o pbkdf2 (werkzeug)."""
    if not doc.get("password"):
        return False
    p = doc["password"]
    if p.startswith("$2") or p.startswith("$2a") or p.startswith("$2b"):
        return bcrypt.check_password_hash(p, password)
    return werkzeug_check_password(p, password)


def _find_and_migrate_legacy_user(identifier, password):
    """Busca usuario en colecciones legacy ('user', 'users') y lo migra a app_users si la contraseña es correcta."""
    try:
        uri = current_app.config.get("MONGODB_SETTINGS", {}).get("host") or os.getenv(
            "MONGO_URI"
        )
        if not uri:
            print("[login] legacy: MONGO_URI no definido")
            return None
        client = MongoClient(uri)
        db_name = current_app.config.get("MONGODB_SETTINGS", {}).get("db", "test")
        mongo_db = client[db_name]

        # 1) Buscar en 'user' (bcrypt)
        for coll_name in ("user", "users"):
            coll = mongo_db[coll_name]
            doc = coll.find_one(
                {
                    "$or": [{"email": identifier}, {"username": identifier}],
                    "username": {"$exists": True},
                    "password": {"$exists": True},
                }
            )
            if not doc:
                continue
            if not _check_password_any(doc, password):
                print(
                    f"[login] legacy: contraseña incorrecta para {doc.get('username')}"
                )
                return None
            # Migrar a app_users (rehashear con bcrypt si es pbkdf2)
            existing = (
                User.objects(email=doc["email"]).first()
                or User.objects(username=doc["username"]).first()
            )
            if existing:
                existing.set_password(password)  # actualizar a bcrypt
                existing.save()
                return existing
            user = User(
                username=doc["username"],
                email=doc["email"],
                is_admin=doc.get("is_admin", False),
            )
            user.set_password(password)  # bcrypt
            user.image_file = (
                doc.get("image_file") or doc.get("foto_perfil") or "default.jpg"
            )
            user.address = doc.get("address")
            user.phone = doc.get("phone")
            user.save()
            return user

        print(f"[login] legacy: no encontrado en 'user' ni 'users' (db={db_name})")
        return None
    except Exception as e:
        print(f"[login] Error en migración legacy: {e}")
        return None


def _sync_legacy_password_to_app_user(identifier, password):
    """Actualiza la contraseña en app_users desde legacy cuando el usuario ya existía (p.ej. por OAuth)."""
    try:
        uri = current_app.config.get("MONGODB_SETTINGS", {}).get("host") or os.getenv(
            "MONGO_URI"
        )
        if not uri:
            return
        client = MongoClient(uri)
        mongo_db = client[
            current_app.config.get("MONGODB_SETTINGS", {}).get("db", "test")
        ]
        for coll in (mongo_db["user"], mongo_db["users"]):
            doc = coll.find_one(
                {
                    "$or": [{"email": identifier}, {"username": identifier}],
                    "username": {"$exists": True},
                    "password": {"$exists": True},
                }
            )
            if doc and _check_password_any(doc, password):
                app_user = (
                    User.objects(email=doc["email"]).first()
                    or User.objects(username=doc["username"]).first()
                )
                if app_user:
                    app_user.set_password(password)
                    app_user.save()
                return
    except Exception as e:
        print(f"[login] Error sincronizando contraseña: {e}")


def _is_safe_redirect(next_url):
    """Solo permite redirecciones a rutas internas (no absolutas externas)."""
    if not next_url:
        return False
    parsed = urlparse(next_url)
    return not parsed.netloc or parsed.netloc in ("", request.host)


@main.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        next_page = request.args.get("next")
        if next_page and _is_safe_redirect(next_page):
            return redirect(next_page)
        return redirect(url_for("main.home"))

    form = LoginForm(meta={"csrf": False})
    if request.method == "POST" and not form.validate_on_submit():
        print(f"[login] POST pero validación fallida: {form.errors}")
    if form.validate_on_submit():
        identifier = form.email_or_username.data
        # Solo documentos con username/password (excluye usuarios OAuth de Better-Auth)
        q = dict(username__exists=True, password__exists=True)
        user = (
            User.objects(**q, email=identifier).first()
            or User.objects(**q, username=identifier).first()
        )
        if not user:
            user = _find_and_migrate_legacy_user(identifier, form.password.data)
        elif not user.check_password(form.password.data):
            _sync_legacy_password_to_app_user(identifier, form.password.data)
            user = (
                User.objects(**q, email=identifier).first()
                or User.objects(**q, username=identifier).first()
            )
        pwd_ok = user and user.check_password(form.password.data)
        print(f"[login] identifier={identifier!r} found={bool(user)} pwd_ok={pwd_ok}")
        if pwd_ok:
            login_user(user, remember=bool(form.remember.data))
            flash(f"¡Bienvenido de nuevo, {user.username}!", "success")
            next_page = request.args.get("next")
            if next_page and _is_safe_redirect(next_page):
                return redirect(next_page)
            return redirect(url_for("main.home"))
        flash("Login fallido. Por favor comprueba usuario y contraseña.", "danger")
    better_auth_url = current_app.config.get("BETTER_AUTH_URL", "http://localhost:3000")
    flask_callback = request.url_root.rstrip("/") + url_for("main.auth_callback")

    # Redirect-through para pasar el token JWT (cross-origin)
    oauth_callback = f"{better_auth_url}/redirect-to-client?clientCallback={quote(flask_callback, safe='')}"
    return render_template(
        "login.html",
        title="Login",
        form=form,
        better_auth_url=better_auth_url,
        oauth_callback=oauth_callback,
    )


@main.route("/auth/callback")
def auth_callback():
    from app.auth_client import verify_session

    token = request.args.get("token")
    err = request.args.get("error")
    if err:
        if err == "no_token":
            print(
                "[auth_callback] redirect-to-client no obtuvo token de /api/auth/token"
            )
        flash("Error en la autenticación social.", "danger")
        return redirect(url_for("main.login"))
    payload = verify_session(token) if token else None
    if not token:
        print("[auth_callback] No se recibió token en la URL")
    elif not payload:
        print("[auth_callback] Token recibido pero verify_session falló")
    if payload:
        email = payload.get("email") or (payload.get("user") or {}).get("email")
        if email:
            user = User.objects(email=email).first()
            if not user:
                name = (
                    payload.get("name")
                    or (payload.get("user") or {}).get("name")
                    or email.split("@")[0]
                )
                user = User(username=name, email=email)
                user.set_password(os.urandom(16).hex())
                user.save()
            login_user(user)
            flash(f"¡Hola {user.username}, has entrado con éxito!", "success")
            return redirect(url_for("main.home"))
    flash("Error en la autenticación social.", "danger")
    return redirect(url_for("main.login"))


@main.route("/containers")
@login_required
def list_containers():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("search", "")
    form = SearchContainerForm()
    if search_query:
        containers = Container.objects(
            (Q(name__icontains=search_query) | Q(location__icontains=search_query))
            & Q(user=current_user._get_current_object())
        ).paginate(page=page, per_page=10)
    else:
        containers = Container.objects(
            user=current_user._get_current_object()
        ).paginate(page=page, per_page=10)
    return render_template(
        "list_containers.html",
        title="Mis Contenedores",
        containers=containers,
        form=form,
        search_query=search_query,
    )


@main.route("/create_container", methods=["GET", "POST"])
@login_required
def create_container():
    form = ContainerForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data) if form.picture.data else None
        container_name = form.name.data
        qr_file = f"{slugify(container_name)}.png"
        save_qr_image(f"Contenedor: {container_name}", qr_file)
        container = Container(
            name=container_name,
            location=form.location.data,
            items=form.items.data.split(","),
            image_file=picture_file,
            qr_image=qr_file,
            user=current_user._get_current_object(),
        )
        container.save()
        flash("Contenedor creado!", "success")
        return redirect(url_for("main.list_containers"))
    return render_template("create_container.html", title="Crear", form=form)


@main.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.save()
        flash("Cuenta actualizada!", "success")
        return redirect(url_for("main.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    img = url_for("static", filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Cuenta", form=form, image_file=img)


@main.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            current_user.save()
            flash("Password actualizado!", "success")
            return redirect(url_for("main.account"))
        flash("Password actual incorrecto.", "danger")
    return render_template("change_password.html", title="Password", form=form)


@main.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    user.delete()
    flash("Tu cuenta ha sido eliminada.", "info")
    return redirect(url_for("main.home"))


@main.route("/contacto", methods=["GET", "POST"])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(
            f"Contacto de {form.name.data}",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[current_app.config["CONTACT_MAIL_RECIPIENT"]],
            reply_to=form.email.data,
        )
        msg.body = form.message.data
        try:
            mail.send(msg)
            flash("Enviado!", "success")
            return redirect(url_for("main.home"))
        except:
            flash("Error al enviar mail.", "danger")
    return render_template("contacto.html", title="Contacto", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@main.route("/container/<container_id>")
@login_required
def container_detail(container_id):
    container = Container.objects(id=container_id).first_or_404()
    return render_template("container_detail.html", container=container)


@main.route("/containers/<container_id>/edit", methods=["GET", "POST"])
@login_required
def edit_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    if container.user != current_user:
        abort(403)
    form = ContainerForm()
    if form.validate_on_submit():
        container.name, container.location, container.items = (
            form.name.data,
            form.location.data,
            form.items.data.split(","),
        )
        container.save()
        flash("Actualizado!", "success")
        return redirect(url_for("main.list_containers"))
    elif request.method == "GET":
        form.name.data, form.location.data, form.items.data = (
            container.name,
            container.location,
            ",".join(container.items),
        )
    return render_template(
        "edit_container.html", title="Editar", form=form, container=container
    )


@main.route("/containers/<container_id>/delete", methods=["POST"])
@login_required
def delete_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    if container.user != current_user:
        abort(403)
    container.delete()
    flash("Eliminado.", "success")
    return redirect(url_for("main.list_containers"))


@main.route("/download_container/<container_id>")
@login_required
def download_container(container_id):
    c = Container.objects(id=container_id).first_or_404()
    p = os.path.join(current_app.root_path, "static/qr_codes", c.qr_image)
    return send_file(p, as_attachment=True) if os.path.exists(p) else "Error"


@main.route("/print_container/<container_id>")
@login_required
def print_container(container_id):
    c = Container.objects(id=container_id).first_or_404()
    return render_template("print_container.html", container=c)


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        flash("Tu cuenta ha sido creada. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@main.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    return render_template("reset_request.html", form=form)
