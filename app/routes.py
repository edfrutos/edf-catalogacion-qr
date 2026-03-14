from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app, make_response, send_file, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, mail # bcrypt aquí es la instancia de Flask-Bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, ContainerForm, RequestResetForm, ResetPasswordForm, DeleteAccountForm, ContactForm, ChangePasswordForm, UpdateUserForm, SearchContainerForm
from app.models import User, Container
from app.main.utils import save_picture, send_reset_email, save_qr_image, slugify # Añadir slugify a la importación
from flask_mail import Message
import qrcode
# import base64 # No parece usarse
# from io import BytesIO # No parece usarse
# La línea de werkzeug.security ya fue eliminada o comentada en un paso anterior, se confirma que no está.
from mongoengine.queryset.visitor import Q
import secrets
import os
from PIL import Image
import re
import uuid # Importar uuid
import unicodedata

# slugify, save_picture, save_qr_image movidas a app.main.utils

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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data) # Usar el método del modelo
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
                  sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com'),
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
        contact_sender_email = form.email.data
        msg = Message(subject=f"Mensaje de Contacto de: {form.name.data}",
                      sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com'),
                      recipients=[current_app.config.get('CONTACT_MAIL_RECIPIENT', 'admin@example.com')],
                      reply_to=contact_sender_email)
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
        
        picture_file = None
        if form.picture.data:
            picture_file = save_picture(form.picture.data)

        container_name = form.name.data
        container_location = form.location.data
        container_items_str = form.items.data

        qr_filename = f"{slugify(container_name)}.png"
        qr_data = f"Contenedor: {container_name}\nUbicación: {container_location}\nObjetos: {container_items_str}"

        # Usar la función save_qr_image actualizada
        generated_qr_path = save_qr_image(qr_data, qr_filename) # save_qr_image ahora devuelve la ruta o None

        if not generated_qr_path:
            flash('Error al generar o guardar el código QR.', 'danger')
            # Decidir si se quiere continuar sin QR o retornar
            return render_template('create_container.html', title='Crear Contenedor', form=form)

        container = Container(
            name=container_name,
            location=container_location,
            items=container_items_str.split(","),
            image_file=picture_file,
            qr_image=qr_filename, # Guardar solo el nombre del archivo
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
    original_qr_filename = container.qr_image
    original_container_name_slug = slugify(container.name) + ".png" if container.name else None

    if form.validate_on_submit():
        new_name = form.name.data
        new_location = form.location.data
        new_items_str = form.items.data

        name_changed = container.name != new_name

        container.name = new_name
        container.location = new_location
        container.items = new_items_str.split(',')

        if form.picture.data:
            # Aquí se podría eliminar la foto de perfil anterior si existe y es diferente
            picture_file = save_picture(form.picture.data)
            container.image_file = picture_file

        # Manejo del QR
        new_qr_filename_base = slugify(new_name)
        new_qr_filename = f"{new_qr_filename_base}.png"
        
        qr_data = f"Contenedor: {new_name}\nLocalización: {new_location}\nObjetos: {new_items_str}"

        # Si el nombre del contenedor cambió, el nombre del archivo QR también debería cambiar.
        # O si el QR original no existe o tiene un nombre basado en el slug antiguo.
        if name_changed or not original_qr_filename or original_qr_filename != new_qr_filename:
            # Eliminar el QR antiguo si existe y el nombre ha cambiado
            if name_changed and original_qr_filename:
                old_qr_path = os.path.join(current_app.root_path, 'static', 'qr_codes', original_qr_filename)
                if os.path.exists(old_qr_path):
                    try:
                        os.remove(old_qr_path)
                        print(f"Eliminado QR antiguo: {old_qr_path}") # Log
                    except OSError as e:
                        print(f"Error eliminando QR antiguo {old_qr_path}: {e}") # Log

            generated_qr_path = save_qr_image(qr_data, new_qr_filename) # Guardar nuevo QR
            if generated_qr_path:
                container.qr_image = new_qr_filename
            else:
                flash('Error al generar o guardar el nuevo código QR.', 'danger')
        else:
            # El nombre no cambió, pero otros datos podrían haberlo hecho, así que regeneramos el QR
            # con el mismo nombre de archivo.
            save_qr_image(qr_data, original_qr_filename) # Sobrescribe el QR existente
            container.qr_image = original_qr_filename # Asegurar que sigue siendo el mismo

        container.save()
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

    qr_filename_to_delete = container.qr_image # Guardar antes de borrar el objeto de BD

    container.delete() # Eliminar de la BD

    # Eliminar el archivo QR asociado si existe
    if qr_filename_to_delete:
        qr_path_to_delete = os.path.join(current_app.root_path, 'static', 'qr_codes', qr_filename_to_delete)
        if os.path.exists(qr_path_to_delete):
            try:
                os.remove(qr_path_to_delete)
                print(f"Eliminado archivo QR: {qr_path_to_delete}") # Log
            except OSError as e:
                print(f"Error eliminando archivo QR {qr_path_to_delete}: {e}") # Log
        else:
            print(f"Archivo QR no encontrado para eliminar: {qr_path_to_delete}") # Log

    flash('Tu contenedor y su código QR asociado han sido eliminados!', 'success')
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
        if current_user.check_password(form.current_password.data): # Usar el método del modelo
            current_user.set_password(form.new_password.data) # Usar el método del modelo
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

# Las funciones save_picture y save_qr_image han sido movidas a app.main.utils
# y se importan desde allí.