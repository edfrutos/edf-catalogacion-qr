import os
import secrets
from PIL import Image
from flask import current_app, url_for
from flask_mail import Message
from app import mail
import qrcode
import uuid # Importar uuid
import re # Para slugify
import unicodedata # Para slugify

def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def save_picture(form_picture):
    # Generar un nombre de archivo único usando UUID
    random_name = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_name + f_ext.lower() # Guardar extensión en minúsculas

    profile_pics_dir = os.path.join(current_app.root_path, 'static', 'profile_pics')
    if not os.path.exists(profile_pics_dir):
        try:
            os.makedirs(profile_pics_dir)
        except OSError as e:
            # Log o manejo de error, podría ser importante si el dir no se puede crear
            print(f"Error creando directorio {profile_pics_dir}: {e}") # Log
            # Considerar retornar None o lanzar la excepción
            # return None

    picture_path = os.path.join(profile_pics_dir, picture_fn)

    output_size = (800, 800)  # Ajustar la resolución según sea necesario
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

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

    qr_dir = os.path.join(current_app.root_path, 'static', 'qr_codes')
    if not os.path.exists(qr_dir):
        try:
            os.makedirs(qr_dir)
        except OSError as e:
            print(f"Error creating directory {qr_dir}: {e}")
            return None # Fallar si no se puede crear el directorio

    # container_name aquí es en realidad el qr_filename (ej: "mi-contenedor.png")
    # ya que las rutas lo llamarán con el nombre de archivo slugificado y con .png
    qr_path = os.path.join(qr_dir, container_name)
    try:
        img.save(qr_path)
        return qr_path
    except Exception as e:
        print(f"Error saving QR image to {qr_path}: {e}")
        return None