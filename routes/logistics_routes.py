from venv import logger
from flask import (
    Blueprint, request, render_template, redirect,
    url_for, flash, current_app, session, abort
)
from datetime import datetime, timedelta
from models import Logistics, LogisticsType, LogisticsStatus, LogisticsType_enum, LogisticsTypeOffer
from models import db
from helpers.decorators import requires_login, makesure_user_logistics, requires_admin, if_completed_logistics

logistics_bp = Blueprint("logistics", __name__)

@makesure_user_logistics
@requires_login
@logistics_bp.route("/logistyka", methods=["GET", "POST"])
def logistics_index():
    # pobieramy z configu nazwę domyślnego użytkownika
    default_user = current_app.config.get('DEFAULT_USER', 'Anonim')

    if request.method == "POST":
        # walidacja pól formularza
        try:
            type_order = LogisticsType(request.form["type_order"])
            subtype_cls = LogisticsType_enum[type_order]
            subtype_enum = subtype_cls(request.form["subtype_order"])
            status = LogisticsStatus("active")  # domyślny status
            quantity = int(request.form["quantity"])
            # offert_type = request.form.get("offert")
            offert_value = request.form.get("offert")
            offert_enum = LogisticsTypeOffer(offert_value) if offert_value else None
            # TODO trzeba poprawić logikę, bo póki co po wypełnieniu formularza dla dt_str i prefferred_time nie wpisuje w bazę danych
            
            dt_str = request.form.get("preferred_time")
            # prefferred_time = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M") if dt_str else None
            preferred_time = None
            if dt_str:
                try:
                    preferred_time = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
                    if preferred_time < datetime.now() + timedelta(hours=8):
                        logger.warning(f"{datetime.now()} | Użytkownik {default_user} | {request.remote_addr} | Data_w_przeszłości | logistyka")
                        flash("Data nie może być w przeszłości.", "error")
                        return redirect(url_for("logistics.logistics_index"))
                except ValueError:
                    logger.warning(f"{datetime.now()} | Użytkownik {default_user} | {request.remote_addr} | Niepoprawny_format_daty | logistyka")
                    flash("Niepoprawny format daty. Użyj formatu YYYY-MM-DDTHH:MM.", "error")
                    return redirect(url_for("logistics.logistics_index"))

        except (KeyError, ValueError):
            logger.warning(f"{datetime.now()} | Użytkownik {default_user} | {request.remote_addr} | Niepoprawne_dane_w_formularzu | logistyka")
            return redirect(url_for("logistics.logistics_index"))
        # tworzymy nowe zlecenie, bez pól z formularza na contractor/principal

        default_user = session.get('username', default_user)

        order = Logistics(
            type_order = type_order,
            subtype_order = subtype_enum.value,
            status = status,
            quantity = quantity,
            contractor = default_user,  # zakładamy, że użytkownik jest zalogowany
            principal = None,  # zakładamy, że użytkownik jest zalogowany
            time_create = datetime.now(),
            # offert_type = offert_type
            offert = offert_enum,
            preferred_time=preferred_time
        )

        db.session.add(order)
        db.session.commit()

        flash("Zlecenie dodane pomyślnie!", "success")
        return redirect(url_for("logistics.logistics_index"))

    # GET — wyświetlamy listę zleceń i formularz
    orders = Logistics.query.all()
    return render_template(
        "logistics.html",
        add_orders = orders,
        now = datetime.now(),
        default_user = default_user
    )
@requires_login
@makesure_user_logistics
@logistics_bp.route("/logistyka/<int:order_id>/edit", methods=["GET", "POST"])
def edit_order(order_id):
    order = Logistics.query.get_or_404(order_id)

    # Sprawdzenie, czy zlecenie jest zakończone
    if order.status == LogisticsStatus.deleted or order.status == LogisticsStatus.disabled:
        logger.warning(f"{datetime.now()} | Próba edycji usuniętego zlecenia przez użytkownika | {request.remote_addr}")
        flash("Nie możesz edytować usuniętego zlecenia.", "error")
        return redirect(url_for("logistics.logistics_index"))

    if order.status == LogisticsStatus.completed:
        logger.warning(f"{datetime.now()} | Próba edycji zlecenia zakończonego przez  użytkownika | {request.remote_addr}")
        flash("Nie możesz edytować zakończonego zlecenia.", "error")
        return redirect(url_for("logistics.logistics_index"))
    if not order.contractor == session.get('username'):
        logger.warning(f"{datetime.now()} | Próba edycji zlecenia przez nieuprawnionego użytkownika | {request.remote_addr}")
        flash("Nie masz uprawnień do edycji tego zlecenia.", "error")
        return redirect(url_for("logistics.logistics_index"))
    if order.status == LogisticsStatus.disabled:
        logger.warning("Decyzja 1.1 - użytkownik zakończył zlecenie")
        return redirect(url_for("logistics.logistics_index"))

    if not order:
        logger.warning(f"{datetime.now()} | Próba edycji nieistniejącego zlecenia | {request.remote_addr}")
        abort(404, "Zlecenie nie istnieje.")


    if request.method == "POST":
        # walidacja pól formularza
        try:
            quantity = int(request.form["quantity"])
            status = LogisticsStatus(request.form["status"])
            if order.status not in [LogisticsStatus.active, LogisticsStatus.completed]:
                # logger.error(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Zlecenie_nie_jest_aktywne_i_nie_można_go_edytować | logistyka", "error")
                raise ValueError("Zlecenie nie jest aktywne i nie można go edytować.")
            if quantity <= 0:
                # logger.error(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Niepoprawna_ilość_w_zleceniu | logistyka", "error")
                raise ValueError("Ilość musi być większa niż zero.")

        except (KeyError, ValueError):
            logger.warning(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Niepoprawne_dane_w_formularzu | logistyka")
            return redirect(url_for("logistics.logistics_index"))
        # aktualizacja pól zlecenia
        order.quantity = quantity
        order.status = status
        order.time_update = datetime.now()

        # Zapisanie zmian w bazie danych
        db.session.commit()
        logger.info(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Zlecenie zaktualizowane pomyślnie! | logistyka")
        return redirect(url_for("logistics.logistics_index"))
    return render_template("logistics_edit.html", order=order)

@requires_login
@makesure_user_logistics
@logistics_bp.route("/logistyka/<int:order_id>/delete", methods=["POST"])
def delete_order(order_id):
    order = Logistics.query.get_or_404(order_id)
    order.status = LogisticsStatus.deleted

    if not order:
        logger.warning(f"{datetime.now()} | Próba usunięcia nieistniejącego zlecenia | {request.remote_addr}")
        abort(404, "Zlecenie nie istnieje.")
        
    if session.get('username') != order.contractor:
        logger.warning(f"{datetime.now()} | Próba usunięcia zlecenia przez nieuprawnionego użytkownika | {request.remote_addr}")
        flash("Nie masz uprawnień do usunięcia tego zlecenia.", "error")
        return redirect(url_for('logistics.logistics_index'))
    
    if order.status == LogisticsStatus.completed:
        logger.warning(f"{datetime.now()} | Próba usunięcia zakończonego zlecenia | {request.remote_addr}")
        flash("Nie możesz usunąć zakończonego zlecenia.", "error")
        return redirect(url_for('logistics.logistics_index'))
    
    if order.status == LogisticsStatus.disabled:
        logger.warning(f"{datetime.now()} | Próba usunięcia wyłączonego zlecenia | {request.remote_addr}")
        flash("Nie możesz usunąć zlecenia, które jest wyłączone.", "error")
        return redirect(url_for('logistics.logistics_index'))
    

    db.session.delete(order)
    db.session.commit()
    logger.info(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Zlecenie usunięte pomyślnie! | logistyka")
    flash("Zlecenie usunięte pomyślnie!", "success")
    return redirect(url_for("logistics.logistics_index"))

@requires_login
@makesure_user_logistics
@logistics_bp.route("/logistyka/<int:order_id>/complete", methods=["POST", "GET"])
def complete_order(order_id):
    order = Logistics.query.get_or_404(order_id)
    username = session.get('username')

    if username == order.contractor:
        logger.warning(f"{datetime.now()} | Próba zakończenia zlecenia przez nieuprawnionego użytkownika | {username}")
        flash("Nie masz uprawnień do zakończenia tego zlecenia.", "error")
        return redirect(url_for('logistics.logistics_index'))

    if order.status == LogisticsStatus.deleted:
        logger.warning(f"{datetime.now()} | Próba zakończenia usuniętego zlecenia | {request.remote_addr}")
        flash("Nie możesz zakończyć usuniętego zlecenia.", "error")
        return redirect(url_for('logistics.logistics_index'))

    if order.status == LogisticsStatus.disabled:
        logger.warning(f"{datetime.now()} | Próba zakończenia wyłączonego zlecenia | {request.remote_addr}")
        flash("Nie możesz zakończyć zlecenia, które jest wyłączone.", "error")
        return redirect(url_for('logistics.logistics_index'))

    # Działa i dla GET, i dla POST
    order.principal = username
    order.status = LogisticsStatus.completed
    db.session.commit()
    logger.info(f"{datetime.now()} | użytkownik {order.contractor} | {request.remote_addr} | Zlecenie zakończone! | logistyka")
    return redirect(url_for("logistics.logistics_index"))
