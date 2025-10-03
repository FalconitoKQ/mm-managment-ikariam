# routes/auth_routes.py
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from datetime import datetime
from models import db
from models.user import User
from models.role import Role
from models.license_token import LicenseToken
from helpers.decorators import requires_login
from models import logger
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/rejestracja', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Tworzymy instancję formularza
    logger.info(f'{datetime.now()} | Wyświetlenie formularza rejestracji przez IP: {request.remote_addr}')
    if form.validate_on_submit():
        # 1. Pobierz dane z pól formularza
        license_token_input = form.license_token.data
        username = form.username.data
        password = form.password.data

        if not license_token_input:
            flash('Musisz podać token licencyjny.', 'error')
            return redirect(url_for('auth.register'))

        # 2. Sprawdź token licencyjny
        token_entry = LicenseToken.query.filter_by(token=license_token_input, used=False).first()
        if not token_entry or token_entry.expires_at < datetime.utcnow():
            flash('Niepoprawny lub wygasły token licencyjny.', 'error')
            return redirect(url_for('auth.register'))

        # 3. Sprawdź, czy użytkownik już istnieje
        if User.query.filter_by(username=username).first():
            logger.warning(f'{datetime.now()} | Użytkownik {username} o tej nazwie już istnieje.', 'error')
            return redirect(url_for('auth.register'))

        # 4. Tworzenie nowego użytkownika
        new_user = User(username=username)
        new_user.set_password(password)

        # 5. Przypisanie roli domyślnej
        default_role = Role.query.filter_by(name='default').first()
        if not default_role:
            default_role = Role(name='default')
            db.session.add(default_role)
            db.session.commit()
        new_user.roles.append(default_role)
        db.session.add(new_user)

        # 6. Oznaczenie tokenu jako użyty
        token_entry.used = True
        db.session.commit()

        logger.info(f'{datetime.now()} | Użytkownik {username} został zarejestrowany.')
        return redirect(url_for('auth.login'))

    # Gdy GET lub walidacja się nie powiodła – wyświetlamy szablon z formularzem
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    logger.info(f'{datetime.now()} | Wyświetlenie formularza logowania przez IP: {request.remote_addr}')

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            logger.warning(f'{datetime.now()} | Próba logowania nieudana dla użytkownika {username}.')
            return redirect(url_for('auth.login'))

        session['login'] = True
        session['username'] = user.username
        logger.info(f'{datetime.now()} | Użytkownik {username} zalogowany pomyślnie.')
        return redirect(url_for('battle.index'))
        

        
    return render_template('identificat.html', form=form)


# Temat do przemyślenia; nie wiem jak przeprowadzić reset hasła, można by było zrobić reset przez bota na discord
@auth_bp.route('/zmiana_hasla', methods=['GET', 'POST'])
@requires_login
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        user = User.query.filter_by(username=session['username']).first()
        if not user or not user.check_password(current_password):
            flash('Błędne hasło.', 'error')
            return redirect(url_for('auth.change_password'))
        user.set_password(new_password)
        db.session.commit()
        flash('Hasło zostało zmienione pomyślnie.', 'success')
        return redirect(url_for('battle.index'))
    return render_template('change_password.html')

@auth_bp.route('/logout')
@requires_login
def logout():
    # Wylogowanie użytkownika
    session.clear()
    logger.info(f'{datetime.now()} | Użytkownik {session.get("username")} wylogowany.')
    return redirect(url_for('auth.login'))

class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')

class RegisterForm(FlaskForm):
    license_token = StringField('Token licencyjny', validators=[DataRequired()])
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj się')