# models/zgloszenie.py
from datetime import datetime
from models import db
from enum import Enum

class Status(Enum):
    OPEN = 'OPEN', 'Otwarte'
    IN_PROGRESS = 'IN_PROGRESS', 'W trakcie / Do realizacji'
    CLOSED = 'CLOSED', 'Zakończone'

class Zgloszenie(db.Model):
    __tablename__ = 'zgloszenia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tresc = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    # Relacja do użytkownika składającego zgłoszenie
    status = db.Column(db.String(50), nullable=False, default=Status.OPEN.value[0])

    def __repr__(self):
        return f"<Zgloszenie id={self.id} user_id={self.user_id}>"
