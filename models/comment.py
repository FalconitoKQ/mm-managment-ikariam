from datetime import datetime
from models import db
from models.battle import Add_battle_db

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    battle_id = db.Column(db.Integer, db.ForeignKey('add_battle_db.id_add_battle_db'), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # relacje do bitwy
    battle = db.relationship('Add_battle_db', back_populates='comments')
    