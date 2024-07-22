from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app, make_response, send_file, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, ContainerForm, RequestResetForm, ResetPasswordForm, DeleteAccountForm, ContactForm, ChangePasswordForm, UpdateUserForm, SearchContainerForm
from app.models import User, Container
from app.main.utils import save_picture, send_reset_email, save_qr_image
from flask_mail import Message
import qrcode
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine.queryset.visitor import Q
import secrets
import os
from PIL import Image

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    session.pop('show_welcome_modal', None)  # Limpiar la sesión de modal de bienvenida
    return render_template('home.html', title='Inicio')

@main.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash('Tu cuenta ha sido creada! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email_or_username.data).first() or User.objects(username=form.email_or_username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Inicio de sesión no exitoso. Por favor verifica tu correo/usuario y contraseña.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    session['show_farewell_modal'] = True
    session['show_welcome_modal'] = True  # Esto puede ajustarse según sea necesario
    return redirect(url_for('main.home'))

@main.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        current_user.phone = form.phone.data
        current_user.save()
        flash('Tu cuenta ha sido actualizada!', 'success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data = current_user.address
        form.phone.data = current_user.phone
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Cuenta', image_file=image_file, form=form)

@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Se ha enviado un email con instrucciones para restablecer tu contraseña.', 'info')
            return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Restablecer Contraseña', form=form)

@main.route("/change_pass/<token>", methods=['GET', 'POST'])
def change_pass(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Token inválido o expirado', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save()
        flash('Tu contraseña ha sido actualizada! Ahora puedes ingresar', 'success')
        return redirect(url_for('main.login'))
    return render_template('change_password2.html', title='Cambiar Contraseña', form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Solicitud de restablecimiento de contraseña',
                  sender='admin@edefrutos.me',
                  recipients=[user.email])
    msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{url_for('main.change_pass', token=token, _external=True)}

Si no solicitaste este cambio, simplemente ignora este mensaje y no se realizará ningún cambio.
'''
    mail.send(msg)
    
@main.route("/contacto", methods=['GET', 'POST'])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(form.name.data + ' ha enviado un mensaje',
                      sender='noreply@demo.com',
                      recipients=['admin@edfdivi.es'])
        msg.body = f'''
        Nombre: {form.name.data}
        Email: {form.email.data}
        Mensaje: {form.message.data}
        '''
        mail.send(msg)
        flash('Tu mensaje ha sido enviado!', 'success')
        return redirect(url_for('main.home'))
    return render_template('contacto.html', title='Contacto', form=form)

@main.route("/container/<container_id>", methods=["GET"])
@login_required
def container_detail(container_id):
    try:
        container = Container.objects.get(id=container_id)
        return render_template('container_detail.html', container=container)
    except Container.DoesNotExist:
        abort(404)

@main.route("/create_container", methods=["GET", "POST"])
@login_required
def create_container():
    form = ContainerForm()
    if form.validate_on_submit():
        if Container.objects(name=form.name.data).first():
            flash('El nombre del contenedor ya está en uso. Por favor elige otro.', 'danger')
            return redirect(url_for('main.create_container'))

        picture_file = None
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        
        # Generar el código QR
        qr_data = f"Contenedor: {form.name.data}\nUbicación: {form.location.data}\nObjetos: {form.items.data}"
        qr_img = qrcode.make(qr_data)
        qr_img_path = os.path.join('app', 'static', 'qr_codes', f"{form.name.data}.png")
        qr_img.save(qr_img_path)

        container = Container(
            name=form.name.data,
            location=form.location.data,
            items=form.items.data.split(","),
            image_file=picture_file,
            qr_image=f"{form.name.data}.png",
            user=current_user._get_current_object()
        )
        try:
            container.save()
            flash("Contenedor creado exitosamente", "success")
            return redirect(url_for('main.list_containers'))
        except Exception as e:
            flash(f'Error al crear el contenedor: {str(e)}', 'danger')
    return render_template('create_container.html', title='Crear Contenedor', form=form)

@main.route("/download_container/<container_id>")
@login_required
def download_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    qr_path = os.path.join(current_app.root_path, 'static/qr_codes', container.qr_image)
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True, download_name=f'{container.name}.png')
    else:
        flash('QR code no encontrado', 'danger')
        return redirect(url_for('main.container_detail', container_id=container_id))

@main.route("/containers", methods=['GET', 'POST'])
@login_required
def list_containers():
    form = ContainerForm()
    search_query = request.args.get('search', '')
    if search_query:
        containers = Container.objects(
            (Q(name__icontains=search_query) | Q(location__icontains=search_query) | Q(items__icontains=search_query)) & Q(user=current_user._get_current_object())
        )
    else:
        containers = Container.objects(user=current_user._get_current_object())
    return render_template('list_containers.html', title='Mis Contenedores', containers=containers, form=form)

@main.route("/containers/<container_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    if container.user != current_user:
        abort(403)
    form = ContainerForm()
    if form.validate_on_submit():
        container.name = form.name.data
        container.location = form.location.data
        container.items = form.items.data.split(',')
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            container.image_file = picture_file
        container.save()
        
        # Generar y guardar el código QR actualizado
        data = f"Nombre: {container.name}\nLocalización: {container.location}\nObjetos: {', '.join(container.items)}"
        save_qr_image(data, container.name)
        flash('Contenedor actualizado con éxito!', 'success')
        return redirect(url_for('main.list_containers'))
    elif request.method == 'GET':
        form.name.data = container.name
        form.location.data = container.location
        form.items.data = ', '.join(container.items)
    return render_template('edit_container.html', title='Editar Contenedor', form=form)

@main.route("/containers/<container_id>/delete", methods=['POST'])
@login_required
def delete_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    if container.user != current_user:
        abort(403)
    container.delete()
    flash('Tu contenedor ha sido eliminado!', 'success')
    return redirect(url_for('main.list_containers'))

@main.route("/print_container/<container_id>")
@login_required
def print_container(container_id):
    container = Container.objects(id=container_id).first_or_404()
    qr_path = os.path.join(current_app.root_path, 'static/qr_codes', container.qr_image)
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True, download_name=f"{container.name}.png")
    else:
        flash('Código QR no encontrado', 'danger')
        return redirect(url_for('main.container_detail', container_id=container_id))

@main.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            current_user.save()
            flash('Tu contraseña ha sido actualizada!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash('Contraseña actual incorrecta', 'danger')
    return render_template('change_password.html', title='Cambiar Contraseña', form=form)

@main.route("/delete_account", methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data:
            user = current_user._get_current_object()
            containers = Container.objects(user=user)
            for container in containers:
                container.delete()
            user.delete()
            flash('Tu cuenta y todos tus contenedores han sido eliminados.', 'success')
            return redirect(url_for('main.home'))
    return render_template('delete_account.html', title='Eliminar Cuenta', form=form)

@main.route("/search_container", methods=['GET', 'POST'])
@login_required
def search_container():
    form = SearchContainerForm()
    search_query = request.args.get('search', '')
    if search_query:
        containers = Container.objects(
            (Q(name__icontains=search_query) | Q(location__icontains=search_query) | Q(items__icontains=search_query)) & Q(user=current_user._get_current_object())
        )
    else:
        containers = Container.objects(user=current_user._get_current_object())
    return render_template('search_container.html', title='Buscar Contenedor', containers=containers, form=form)

@main.route("/welcome")
@login_required
def welcome():
    return render_template('welcome.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (800, 800)  # Adjust the resolution as needed
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_qr_image(data, container_name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Make QR code larger
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    qr_path = os.path.join(current_app.root_path, 'static/qr_codes', container_name + '.png')
    img.save(qr_path)
    return qr_path