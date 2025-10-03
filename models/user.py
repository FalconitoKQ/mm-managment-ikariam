import enum
from models import db, roles_users
from werkzeug.security import generate_password_hash, check_password_hash

class UserStatus(enum.Enum):
    active = 'active'
    disabled = 'disabled'
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    status_user = db.Column(db.Enum(UserStatus), default=UserStatus.active, nullable=False)
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
