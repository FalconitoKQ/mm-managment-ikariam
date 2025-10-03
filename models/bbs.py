# models/bbs.py
from datetime import datetime
from models import db

class Bbs(db.Model):
    __tablename__ = 'battleshipstock'
    id_bbs = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_battle = db.Column(db.Integer, db.ForeignKey('add_battle_db.id_add_battle_db'), nullable=False)
    # Pola zasobów statków
    stock_taran_parowy = db.Column(db.Integer, default=0)
    stock_okret_z_taranem = db.Column(db.Integer, default=0)
    stock_krazownik = db.Column(db.Integer, default=0)
    stock_balonowiec = db.Column(db.Integer, default=0)
    # Pola czasów rund
    time_round_for_taran_parowy = db.Column(db.DateTime, default=datetime.utcnow)
    time_round_for_okret_z_taranem = db.Column(db.DateTime, default=datetime.utcnow)
    time_round_for_krazownik = db.Column(db.DateTime, default=datetime.utcnow)
    time_round_for_balonowiec = db.Column(db.DateTime, default=datetime.utcnow)
    # Pola liczby rund
    number_of_rounds_for_taran_parowy = db.Column(db.Integer)
    number_of_rounds_for_okret_z_taranem = db.Column(db.Integer)
    number_of_rounds_for_krazownik = db.Column(db.Integer)
    number_of_rounds_for_balonowiec = db.Column(db.Integer)
    # Relacja z bitwą (backref z Add_battle_db.bbs_entries)
    battle = db.relationship('Add_battle_db', backref='bbs_entries')
