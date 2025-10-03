# models/slot.py
from models import db

class Slot(db.Model):
    __tablename__ = 'slots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String, nullable=False)
    user = db.Column(db.String(80), nullable=True)
    units = db.Column(db.Integer, nullable=True)
    battle_id = db.Column(db.Integer, db.ForeignKey('add_battle_db.id_add_battle_db'), nullable=False)
    # Relacja z bitwą (backref z Add_battle_db.slots)
    battle = db.relationship('Add_battle_db', backref='slots')
