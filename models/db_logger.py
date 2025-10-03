import logging
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# Dodajemy konfigurację loggera
logger = logging.getLogger('moja_aplikacja')
logger.setLevel(logging.DEBUG)

# Konfiguracja handlera - wyświetlanie logów w konsoli
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
