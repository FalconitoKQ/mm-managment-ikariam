from datetime import datetime
from models import db

class LicenseToken(db.Model):
    __tablename__ = 'licence_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<LicenseToken id={self.id} token={self.token} used={self.used}>"
