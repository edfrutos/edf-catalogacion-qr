from itsdangerous import TimedSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from app import db, login_manager, bcrypt

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

class User(db.Document, UserMixin):
    meta = {'collection': 'user', 'strict': False}  # Ignora campos extra (updatedAt, emailVerified, etc.)
    username = db.StringField(max_length=50, unique=True, required=True)
    email = db.EmailField(max_length=50, unique=True, required=True)
    password = db.StringField(required=True)
    image_file = db.StringField(default='default.jpg')
    address = db.StringField()
    phone = db.StringField()
    is_admin = db.BooleanField(default=False)
    
    def set_password(self, password_text):
        """Genera un hash de la contraseña y lo almacena."""
        self.password = bcrypt.generate_password_hash(password_text).decode('utf-8')

    def check_password(self, password_text):
        """Verifica la contraseña proporcionada contra el hash almacenado."""
        return bcrypt.check_password_hash(self.password, password_text)
    
    @staticmethod
    def verify_reset_token(token):
        """Valida un token de restablecimiento de contraseña."""
        s = Serializer(current_app.config['SECRET_KEY'])
        max_age = current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS', 1800)
        try:
            user_id = s.loads(token, max_age=max_age)['user_id']
        except Exception:
            return None
        return User.objects(id=user_id).first()

    def get_reset_token(self):
        """Genera un token de restablecimiento."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': str(self.id)})

class Container(db.Document):
    name = db.StringField(required=True, unique=True)
    location = db.StringField(required=True)
    items = db.ListField(db.StringField(), required=True)
    tags = db.ListField(db.StringField())
    image_file = db.StringField()
    user = db.ReferenceField(User, required=True)
    qr_image = db.StringField()

    def __repr__(self):
        return f"Container('{self.name}', '{self.location}')"
