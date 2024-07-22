from itsdangerous import TimedSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from mongoengine import Document, StringField, EmailField, ListField, BooleanField, ReferenceField, connect, disconnect
import bcrypt
from app import login_manager

DB_URI = "mongodb+srv://edfrutos:8TrFzqaQxiXkyxFy@cluster0.i5wdlhj.mongodb.net/app-qr-catalogacion?retryWrites=true&w=majority&appName=Cluster0"

# Desconectar si ya hay una conexión
disconnect()

# Conectar a la base de datos
connect(host=DB_URI)

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

class User(Document, UserMixin):
    username = StringField(max_length=50, unique=True, required=True)
    email = StringField(max_length=50, unique=True, required=True)
    password = StringField(required=True)
    image_file = StringField(default='default.jpg')
    address = StringField()
    phone = StringField()
    is_admin = BooleanField(default=False)
    
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
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