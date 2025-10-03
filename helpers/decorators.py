# helpers/decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from models.user import User, UserStatus
from models import logger
from datetime import datetime
from models import logistics


def requires_login(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('login'):
            # przekierowanie do strony logowania (z Blueprintu auth)
            return redirect(url_for('auth.login'))

        # Sprawdzenie czy użytkownik jest zalogowany
        # Jeżeli nie to przekierowanie do strony logowania
        username = session.get('username')
        if not username:
            logger.warning(f"{datetime.now()} | Decyzja 1.1: Próba zarejestrowania użytkownika - Brak nazwy użytkownika w sesji.")
            return redirect(url_for('auth.login'))
        
        # Sprawdzenie czy użytkownik istnieje w bazie danych
        # Jeżeli użytkownik nie istnieje to przekierowanie do strony logowania
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.warning(f"{datetime.now()} | Decyzja 1.2: Próba zarejestrowania użytkownika: {username} - Użytkownik nie istnieje.")
            return redirect(url_for('auth.login'))
        
        # Sprawdzenie statusu użytkownika
        # Jeżeli użytkownik nie jest aktywny to przekierowanie do strony logowania
        if user.status_user == UserStatus.disabled:
            logger.warning(f"{datetime.now()} | Decyzja 1.3: Próba zarejestrowania użytkownika - Użytkownik: {username} sesja nieaktywna.")
            return redirect(url_for('auth.login'))
        logger.info(f"{datetime.now()} | Decyzja 1.4: Użytkownik: {username} - Zalogowany.")
        return view_func(*args, **kwargs)
    return wrapper

# Dekorator sprawdzający, czy użytkownik ma uprawnienia administratora.
def requires_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Sprawdzenie, czy użytkownik jest zalogowany
        username = session.get('username')
        # Jeśli nie jest zalogowany, przekierowanie do strony logowania
        if not username:
            return redirect(url_for('auth.login'))
        user = User.query.filter_by(username=username).first()
        # Jeśli użytkownik nie istnieje lub nie ma roli 'admin', przekierowanie do strony głównej
        if not user or not any(role.name == 'admin' for role in user.roles):
            flash("Brak uprawnień administratora.", "error")
            logger.warning(f"{datetime.now()} | Próba dostępu do strony administracyjnej przez nieuprawnionego użytkownika | {username}")
            return redirect(url_for('battle.index'))
        return view_func(*args, **kwargs)
    return wrapper

# Dekorator sprawdzający, czy użytkownik ma dostęp do zleceń logistycznych
# i czy ma uprawnienia do edycji konkretnego zlecenia.
def makesure_user_logistics(view_func):
    @wraps(view_func)
    def wrapper(**kwargs):
        # Sprawdzenie, czy użytkownik jest zalogowany
        username = session.get('username')
        
        # Jeśli nie jest zalogowany, przekierowanie do strony logowania
        if not username:
            logger.warning(f"{datetime.now()} | Próba edycji zlecenia bez zalogowania | {username}")
            return redirect(url_for('logistics.logistics_index'))
        
        # Sprawdzenie, czy użytkownik ma dostęp do zleceń logistycznych
        order_id = kwargs.get('order_id')
        if order_id is None:
            logger.warning(f"{datetime.now()} | Próba edycji zlecenia bez ID | {username}")
            # Zwrócenie błędu 400, jeśli ID zlecenia nie zostało podane
            abort(400, "Brak ID zlecenia.")
        
        # Pobranie zlecenia z bazy danych
        order = logistics.Logistics.query.get(order_id)
        
        # Jeśli zlecenie nie istnieje, zwrócenie błędu 404
        if not order:
            logger.warning(f"{datetime.now()} | Próba edycji zlecenia przez nieuprawnionego użytkownika została odrzucona | {username}")
            abort(403, "Nie masz uprawnień do edycji tego zlecenia.")
        
        # Sprawdzenie, czy użytkownik jest właścicielem zlecenia
        if order.contractor != username:
            logger.warning(f"{datetime.now()} | Próba edycji zlecenia przez nieuprawnionego użytkownika | {username}")
            abort(403, "Nie masz uprawnień do edycji tego zlecenia.")
        return view_func(**kwargs)
    return wrapper

def if_completed_logistics(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        username = session.get('username')
        # Sprawdzenie, czy użytkownik jest zalogowany
        if not username:
            logger.warning(f"{datetime.now()} | Próba przyjęcia zlecenia bez zalogowania | {request.remote_addr}")
            return redirect(url_for('logistics.logistics_index'))
        order_id = kwargs.get('order_id')
        order = logistics.Logistics.query.get(order_id)
        # Sprawdzenie, czy zlecenie istnieje
        if not order:
            logger.warning(f"{datetime.now()} | Próba przyjęcia zlecenia, które nie istnieje | {request.remote_addr}")
            abort(404, "Zlecenie nie istnieje.")
        # Sprawdzenie, czy zlecenie jest już zakończone
        if username != order.contractor:
            logger.warning(f"{datetime.now()} | Próba przyjęcia zlecenia przez nieuprawnionego użytkownika | {request.remote_addr}")
            abort(403, "Nie masz uprawnień do przyjęcia tego zlecenia.")
        # Sprawdzenie, czy użytkownik jest właścicielem zlecenia
        if username == order.contractor:
            logger.warning(f"{datetime.now()} | Próba_przyjęcia_zlecenia_przez_właściciela_zlecenia | {request.remote_addr}")
            return redirect(url_for('logistics.logistics_index'))
        return view_func(*args, **kwargs)
    return wrapper