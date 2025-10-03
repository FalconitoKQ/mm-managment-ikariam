from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify, current_app
from models import db
from models.user import User
from models.role import Role
from helpers.decorators import requires_admin
from services.license_service import generate_license_token
from datetime import datetime
from models.user import UserStatus
from models import logger
from models.battle import Add_battle_db, BattleStatus
from models.bbs import Bbs
from models.logistics import Logistics, LogisticsStatus
from helpers.decorators import requires_login
from models.zgloszenie import Zgloszenie

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_panel', methods=['GET', 'POST'])
@requires_login
@requires_admin
def admin_panel():
    # Logowanie wejścia do panelu
    logger.info(f"{datetime.now()} | IP: {request.remote_addr} | Użytkownik wszedł do panelu administracyjnego.")

    # Pobranie danych: bitwy i zlecenia logistyczne
    battles = Add_battle_db.query.all()
    orders = Logistics.query.all()
    zgloszenia = Zgloszenie.query.order_by(Zgloszenie.data.desc()).all()

    if request.method == 'POST':
        # Przełączanie opcji ukrycia bitew
        hide_battles = True if request.form.get('hide_battles') == 'on' else False
        current_app.config['HIDE_BATTLES'] = hide_battles
        flash("Ustawienie ukrycia bitew zostało zaktualizowane.", "success")
        return redirect(url_for('admin.admin_panel'))

    # Pobranie listy użytkowników
    users = User.query.all()

    # Sprawdzenie, czy bitwy mają być ukryte
    hide_battles = current_app.config.get('HIDE_BATTLES', False)

    # Przekazanie wszystkich zmiennych do szablonu
    return render_template(
        'admin_panel.html',
        users=users,
        battles=battles,
        orders=orders,
        hide_battles=hide_battles,
        zgloszenia=zgloszenia,
        # status=status
    )


@admin_bp.route('/admin/reset_password/<int:user_id>', methods=['POST'])
@requires_login
@requires_admin
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    user.set_password("defaultpassword")
    db.session.commit()
    flash(f'Hasło użytkownika {user.username} zostało zresetowane.', 'success')
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/desactive/ban_user/<int:user_id>', methods=['POST'])
@requires_login
@requires_admin
def desactive_user(user_id: int):
    user = User.query.get_or_404(user_id)
    user.status_user = UserStatus.disabled
    db.session.commit()
    logger.info(f'{datetime.now()} Sesja użytkownika {user.username} została dezaktywowana.')
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/active/unban_user/<int:user_id>', methods=['POST'])
@requires_login
@requires_admin
def active_user(user_id: int):
    user = User.query.get_or_404(user_id)
    user.status_user = UserStatus.active
    db.session.commit()
    logger.info(f'{datetime.now()} Sesja użytkownika {user.username} została aktywowana.')
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/grant_admin/<int:user_id>', methods=['POST'])
@requires_login
@requires_admin
def grant_admin(user_id):
    user = User.query.get_or_404(user_id)
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()
    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.session.commit()
        flash(f'Nadano uprawnienia administratora użytkownikowi {user.username}.', 'success')
    else:
        flash(f'Użytkownik {user.username} ma już rolę administratora.', 'info')
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/generate_token', methods=['GET', 'POST'])
@requires_login
@requires_admin
def generate_token():
    if request.method == 'POST':
        token = generate_license_token(expiration_hours=24)
        flash(f'Wygenerowano token licencyjny: {token}', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('generate_token.html')

@requires_login
@requires_admin
@admin_bp.route('/admin/hide_battles', methods=['POST'])
def hide_battles():
    hide_battles = request.form.get('hide_battles') == 'on'
    from flask import current_app
    current_app.config['HIDE_BATTLES'] = hide_battles
    flash("Ustawienie ukrycia bitew zostało zaktualizowane.", "success")
    return redirect(url_for('admin.admin_panel'))

@requires_login
@requires_admin
@admin_bp.route('/admin/battle_status/<int:battle_id>', methods=['POST'])
def update_battle_status(battle_id):
    battle = Add_battle_db.query.get_or_404(battle_id)
    new_status = request.form.get('battle_status')
    if new_status not in [status.value for status in BattleStatus]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Nieprawidłowy stan bitwy.'}), 400
        flash('Nieprawidłowy stan bitwy.', 'danger')
        return redirect(url_for('admin.admin_panel'))
    battle.battle_status = BattleStatus[new_status]
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': f'Stan bitwy został zaktualizowany na {new_status}.'})
    flash(f'Stan bitwy został zaktualizowany na {new_status}.', 'success')
    return redirect(url_for('admin.admin_panel'))


#TODO: Refactorowanie kodu, aby poprawić czytelność i organizację
#TODO: Trzeba poprawić tutaj logistykę, aby była bardziej przejrzysta i łatwiejsza do zarządzania
@admin_bp.route('/admin/delete/logistics', methods=['GET', 'POST'])
@requires_login
@requires_admin
def admin_logistics():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        new_status = request.form.get('new_status')
        order = Logistics.query.get_or_404(order_id)

        try:
            new_status_enum = LogisticsStatus[new_status]
        except KeyError:
            flash("Nieprawidłowy status zlecenia.", "danger")
            return redirect(url_for('admin.admin_logistics'))

        # 🔒 Walidacja statusów
        if order.status == LogisticsStatus.completed:
            flash(f"Zlecenie {order.id_order} jest zakończone – nie można zmienić jego statusu.", "danger")
            return redirect(url_for('admin.admin_panel'))

        if new_status_enum == LogisticsStatus.deleted:
            if order.status in [LogisticsStatus.active, LogisticsStatus.disabled]:
                order.status = LogisticsStatus.deleted
                logger.info(f"{datetime.now()} | IP: {request.remote_addr} | Zlecenie {order.id_order} zostało oznaczone jako usunięte.")
                db.session.commit()
                flash(f"Zlecenie {order.id_order} zostało usunięte (status: deleted).", "success")
                return redirect(url_for('admin.admin_panel'))
            else:
                flash(f"Nie można usunąć zlecenia {order.id_order} z obecnym statusem {order.status.label}.", "danger")
                return redirect(url_for('admin.admin_panel'))

        # Inne zmiany statusów dozwolone (opcjonalnie)
        order.status = new_status_enum
        if new_status_enum == LogisticsStatus.completed:
            order.time_complete = datetime.utcnow()
        elif new_status_enum == LogisticsStatus.disabled:
            order.time_cancelled = datetime.utcnow()
        elif new_status_enum == LogisticsStatus.active:
            order.time_cancelled = None

        db.session.commit()
        flash(f"Status zlecenia {order.id_order} został zaktualizowany na {order.status.label}.", "success")
        return redirect(url_for('admin.admin_panel'))

    # GET
    orders = Logistics.query.all()
    return render_template('admin_logistics.html', orders=orders)
