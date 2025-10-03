# models/battle.py
from models import db
import enum
from datetime import datetime
from datetime import datetime
from sqlalchemy import func
# from comment import Comment  # jeśli nie chcesz mieć cykliczności, pomiń ten import

class BattleStatus(enum.Enum):
    started = "started"
    finished = "finished"
    cancelled = "cancelled"



class Add_battle_db(db.Model):
    __tablename__ = 'add_battle_db'
    id_add_battle_db = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_name = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    battle_type = db.Column(db.String(50), nullable=False)
    opponent_name = db.Column(db.String(100), nullable=False)
    battle_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=func.current_timestamp())
    comments_text = db.Column(db.Text, nullable=True)
    time_tolerance = db.Column(db.DateTime, nullable=True)
    battle_status = db.Column(db.Enum(BattleStatus), nullable=False, default=BattleStatus.started)

    # 💡 TO DODAJ (relacja do komentarzy):
    comments = db.relationship('Comment', back_populates='battle', cascade='all, delete-orphan')
