# services/license_service.py
import secrets
from models import logger
from datetime import datetime, timedelta
from models import db
from models.license_token import LicenseToken
from models.user import User

def generate_license_token(expiration_hours=24):
    token = secrets.token_urlsafe(32)

    expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
    new_token = LicenseToken(token=token, expires_at=expires_at)
    db.session.add(new_token)
    db.session.commit()

    logger.info(f'{datetime.now()} | Token licencyjny >> {token} << został wygenerowany.')
    return token
