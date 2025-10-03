# routes/report_routes.py
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from models import db
from models.zgloszenie import Zgloszenie, Status
from models.user import User
from helpers.decorators import requires_login

report_bp = Blueprint('report', __name__)

@report_bp.route('/zgloszenie', methods=['GET', 'POST'])
@requires_login
def submit_report():
    if request.method == 'POST':
        tresc = request.form.get("tresc")
        status =  Status.OPEN.value[0]  # Default status for new reports
        if not tresc:
            flash("Treść zgłoszenia nie może być pusta!", "error")
            return render_template("zgloszenie.html")
        nowe_zgloszenie = Zgloszenie(tresc=tresc)
        db.session.add(nowe_zgloszenie)
        db.session.commit()
        flash("Dziękujemy za zgłoszenie!", 'success')
        return redirect(url_for('battle.index'))
    return render_template('zgloszenia.html')

@report_bp.route('/zgloszenia_learn')
@requires_login
def list_reports():
    zgloszenia = Zgloszenie.query.order_by(Zgloszenie.data.desc()).all()
    return render_template("lista_zgloszen.html", zgloszenia=zgloszenia)

@requires_login
@report_bp.route('/zgloszenie_status/<int:id>', methods=['POST'])
def zgloszenie_status(id):
    zgl = Zgloszenie.query.get(id)
    if not zgl:
        return {"message": "Zgłoszenie nie istnieje."}, 404

    new_status = request.form.get("status")
    allowed = [s.value[0] for s in Status]

    if not new_status:
        return {"message": "Nie podano statusu."}, 400
    if new_status not in allowed:
        return {"message": "Nieprawidłowy status."}, 400

    # Logika spójna z Twoją starą trasą
    if zgl.status == Status.CLOSED.value[0]:
        return {"message": "Nie można zmienić statusu zamkniętego zgłoszenia."}, 400
    if zgl.status == Status.IN_PROGRESS.value[0] and new_status == Status.OPEN.value[0]:
        return {"message": "Nie można cofnąć zgłoszenia do statusu Otwarte."}, 400

    zgl.status = new_status
    db.session.commit()
    return {"message": "Status zgłoszenia został zaktualizowany."}

@requires_login
@report_bp.route('/change_report_status/<int:id>')
def change_report_status(id):
    zgloszenie = Zgloszenie.query.get(id)
    if not zgloszenie:
        flash("Zgłoszenie nie istnieje.", "error")

    status_change = request.args.get('status')
    if zgloszenie.status == Status.CLOSED.value[0]:
        flash("Nie można zmienić statusu zamkniętego zgłoszenia.", "error")
        return redirect(url_for('report.list_reports'))
    if zgloszenie.status == Status.IN_PROGRESS.value[0] and status_change == Status.OPEN.value[0]:
        flash("Nie można cofnąć zgłoszenia do statusu Otwarte.", "error")
        return redirect(url_for('report.list_reports'))

    allowed_statuses = [s.value[0] for s in Status]
    if status_change in allowed_statuses:
        zgloszenie.status = status_change
        db.session.commit()
        flash("Status zgłoszenia został zmieniony.", "success")
    elif status_change is None:
        flash("Nie podano statusu do zmiany.", "error")
    else:
        flash("Nieprawidłowy status.", "error")

    # walidacja
    return redirect(url_for('report.list_reports'))