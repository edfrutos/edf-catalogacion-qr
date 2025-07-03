from itsdangerous import TimedSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from mongoengine import Document, StringField, EmailField, ListField, BooleanField, ReferenceField
# La importación 'import bcrypt' se elimina. Usaremos la instancia de app.
from app import login_manager, bcrypt # Importamos la instancia bcrypt de la app

# DB_URI, disconnect() y connect(host=DB_URI) han sido eliminados.
# La conexión será manejada por la fábrica de la aplicación.

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

class User(Document, UserMixin):
    username = StringField(max_length=50, unique=True, required=True)
    email = StringField(max_length=50, unique=True, required=True)
    password = StringField(required=True) # Almacenará el hash generado por Flask-Bcrypt
    image_file = StringField(default='default.jpg')
    address = StringField()
    phone = StringField()
    is_admin = BooleanField(default=False)
    
    def set_password(self, password_text):
        """Genera un hash de la contraseña y lo almacena."""
        self.password = bcrypt.generate_password_hash(password_text).decode('utf-8')

    def check_password(self, password_text):
        """Verifica la contraseña proporcionada contra el hash almacenado."""
        # password_text debe ser una cadena. self.password ya es una cadena (el hash).
        return bcrypt.check_password_hash(self.password, password_text)
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.objects(id=user_id).first()

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': str(self.id)})

class Container(Document):
    name = StringField(required=True, unique=True)
    location = StringField(required=True)
    items = ListField(StringField(), required=True)
    image_file = StringField()
    user = ReferenceField(User, required=True)
    qr_image = StringField()

    def __repr__(self):
        return f"Container('{self.name}', '{self.location}')"