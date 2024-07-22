from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from app.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso. Por favor, elige otro.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está en uso. Por favor, elige otro.')

class LoginForm(FlaskForm):
    email_or_username = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Dirección Postal', validators=[Length(max=100)])
    phone = StringField('Teléfono', validators=[Length(max=15)])
    picture = FileField('Actualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Actualizar')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user:
                raise ValidationError('Ese nombre de usuario ya está en uso. Por favor elija otro.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.objects(email=email.data).first()
            if user:
                raise ValidationError('Ese correo electrónico ya está en uso. Por favor elija otro.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Reinicio de Contraseña')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is None:
            raise ValidationError('No existe una cuenta con ese correo electrónico. Debe registrarse primero.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reiniciar Contraseña')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Cambiar Contraseña')

class ContainerForm(FlaskForm):
    name = StringField('Nombre del Contenedor', validators=[DataRequired(), Length(min=2, max=50)])
    location = StringField('Ubicación', validators=[DataRequired(), Length(min=2, max=100)])
    items = TextAreaField('Objetos (separados por comas)', validators=[DataRequired()])
    picture = FileField('Imagen del Objeto', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Guardar')

class DeleteAccountForm(FlaskForm):
    confirm = BooleanField('Confirmar eliminación de cuenta', validators=[DataRequired()])
    submit = SubmitField('Eliminar Cuenta')

class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class SearchContainerForm(FlaskForm):
    search_query = StringField('Buscar', validators=[DataRequired()])
    submit = SubmitField('Buscar')

class UpdateUserForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Dirección', validators=[DataRequired()])
    phone = StringField('Teléfono', validators=[DataRequired()])
    submit = SubmitField('Actualizar')