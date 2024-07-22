import mongoengine as db
from app import bcrypt
from werkzeug.security import generate_password_hash

DB_URI = "mongodb+srv://edfrutos:8TrFzqaQxiXkyxFy@cluster0.i5wdlhj.mongodb.net/app-qr-catalogacion?retryWrites=true&w=majority"
from mongoengine.connection import disconnect

# Disconnect if already connected
disconnect()

db.connect(host=DB_URI)

class User(db.Document):
    username = db.StringField(max_length=50, unique=True, required=True)
    email = db.StringField(max_length=50, unique=True, required=True)
    password = db.StringField(required=True)
    image_file = db.StringField(default='default.jpg')
    address = db.StringField()
    phone = db.StringField()
    is_admin = db.BooleanField(default=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('$2b$'):
            self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')
        super().save(*args, **kwargs)

def update_user_passwords():
    try:
        users = User.objects()
        for user in users:
            if user.password and not user.password.startswith('$2b$'):
                user.set_password(user.password)
                user.save()
                print(f"Contraseña actualizada para el usuario {user.username}")
    except db.errors.FieldDoesNotExist as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    update_user_passwords()