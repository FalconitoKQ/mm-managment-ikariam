# routes/battle_routes.py
from flask import Blueprint, request, redirect, url_for, render_template, flash, session, jsonify, current_app
from datetime import datetime, timedelta
from models import db
from models.battle import Add_battle_db
from models.bbs import Bbs
from models.slot import Slot
from helpers.decorators import requires_login
from object.BattleShipStock import Battle_ship_stock
from services.slot_service import create_slots_for_battle_shifted
from models.battle import BattleStatus
from models.comment import Comment
# from models.logger import logger
from models import logger

battle_bp = Blueprint('battle', __name__)

@battle_bp.route('/')
@battle_bp.route('/index')
@requires_login
def index():
    if current_app.config.get("HIDE_BATTLES", False):
        flash("Bitew nie wyświetlamy – administrator je ukrył.", "info")
        return render_template('index.html', battles=[], latest_data={})
    battles = Add_battle_db.query.filter(Add_battle_db.battle_status == BattleStatus.started).all()
    latest_data = {}
    for battle in battles:
        latest_entry = Bbs.query.filter_by(id_battle=battle.id_add_battle_db)\
            .order_by(Bbs.id_bbs.desc()).first()
        latest_data[battle.id_add_battle_db] = latest_entry
    return render_template('index.html', title='Strona Główna', battles=battles, latest_data=latest_data)

@battle_bp.route('/battles', methods=['GET'])
@requires_login
def battles_list():
    battles = Add_battle_db.query.filter(Add_battle_db.battle_status == BattleStatus.started).all()
    return render_template('battles_list.html', battles=battles)

@battle_bp.route('/add_battle', methods=['GET', 'POST'])
@requires_login
def add_battle():
    if request.method == 'POST':
        city_name = request.form.get('city')
        coordinates = request.form.get('coordinates')
        battle_type = request.form.get('battle_type')
        opponent_name = request.form.get('opponent_name')
        comments_text = request.form.get('comments')  # ⬅ poprawka

        if not all([city_name, coordinates, battle_type, opponent_name]):
            flash("Wszystkie pola muszą być wypełnione!", "error")
            return render_template('add_battle.html'), 400
        if not city_name:
            flash("Nazwa miasta jest wymagana!", "error")
            return render_template('add_battle.html'), 400
        if not coordinates:
            flash("Współrzędne są wymagane!", "error")
            return render_template('add_battle.html'), 400
        if not battle_type:
            flash("Typ bitwy jest wymagany!", "error")
            return render_template('add_battle.html'), 400
        if not opponent_name:
            flash("Nazwa przeciwnika jest wymagana!", "error")
            return render_template('add_battle.html'), 400
        if not comments_text:
            flash("Komentarz jest wymagany!", "error")
            return render_template('add_battle.html'), 400

        new_battle = Add_battle_db(
            city_name=city_name,
            coordinates=coordinates,
            battle_type=battle_type,
            opponent_name=opponent_name,
            comments_text=comments_text  # ⬅ poprawka
        )
        db.session.add(new_battle)
        db.session.commit()

        create_slots_for_battle_shifted(new_battle.id_add_battle_db)
        flash('Bitwa została dodana pomyślnie. Sloty zostaną wygenerowane dla dni [-1, 0, +1, +2].', 'success')
        return redirect(url_for('battle.battles_list'))

    return render_template('add_battle.html')



@battle_bp.route('/<int:battle_id>/comment', methods=['POST'])
@requires_login
def add_comment(battle_id):
    text = request.form.get('comment', '').strip()  # dostosuj nazwę pola z formy
    if not text:
        flash("Komentarz nie może być pusty", "error")
    else:
        new_comment = Comment(
            battle_id=battle_id,
            user=session.get('username'),
            text=text,
            created_at=datetime.utcnow()
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Komentarz dodany pomyślnie", "success")
    return redirect(url_for('battle.battle_detail', battle_id=battle_id))

@battle_bp.route('/battle/<int:battle_id>', methods=['GET', 'POST'])
@requires_login
def battle_detail(battle_id):
    battle = Add_battle_db.query.get_or_404(battle_id)

    if request.method == 'POST':
        stock_taran_parowy = int(request.form.get('stock_taran_parowy', 0))
        stock_okret_z_taranem = int(request.form.get('stock_okret_z_taranem', 0))
        stock_krazownik = int(request.form.get('stock_krazownik', 0))
        stock_balonowiec = int(request.form.get('stock_balonowiec', 0))

        calc = Battle_ship_stock(stock_taran_parowy, stock_okret_z_taranem, stock_krazownik, stock_balonowiec)
        calc.losses_per_round_in_all_round()
        calc.time_round()

        new_entry = Bbs(
            id_battle=battle_id,
            stock_taran_parowy=stock_taran_parowy,
            stock_okret_z_taranem=stock_okret_z_taranem,
            stock_krazownik=stock_krazownik,
            stock_balonowiec=stock_balonowiec,
            time_round_for_taran_parowy=calc.time_round_for_taran_parowy,
            time_round_for_okret_z_taranem=calc.time_round_for_okret_z_taranem,
            time_round_for_krazownik=calc.time_round_for_krazownik,
            time_round_for_balonowiec=calc.time_round_for_balonowiec,
            number_of_rounds_for_taran_parowy=calc.nirs_taran_parowy,
            number_of_rounds_for_okret_z_taranem=calc.nirs_okret_z_taranem,
            number_of_rounds_for_krazownik=calc.nirs_krazownik,
            number_of_rounds_for_balonowiec=calc.nirs_balonowiec
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Zapisano statystyki statków dla tej bitwy!', 'success')
        return redirect(url_for('battle.battle_detail', battle_id=battle_id))
    
    create_slots_for_battle_shifted(battle_id)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    slots = Slot.query.filter(
        Slot.battle_id == battle_id,
        Slot.date >= yesterday,
        Slot.date <= day_after_tomorrow
    ).order_by(Slot.date, Slot.time).all()

    latest_stats = Bbs.query.filter_by(id_battle=battle_id).order_by(Bbs.id_bbs.desc()).first()
    comments = battle.comments  # ← tylko to dodane

    return render_template(
        'battle_detail.html',
        battle=battle,
        battleship=latest_stats,
        history=[],
        slots=slots,
        comments=comments  # ← i to
    )


@battle_bp.route('/signup_multiple_slots/<int:battle_id>', methods=['POST'])
@requires_login
def signup_multiple_slots(battle_id):
    slot_ids = request.form.getlist('slot_ids')
    username = session.get('username')
    units = request.form.get('units')
    if not units or not units.isdigit():
        flash('Ilość jednostek musi być liczbą całkowitą.', 'error')
        return redirect(url_for('battle.battle_detail', battle_id=battle_id))
    units = int(units)
    
    taken_slots = []
    for slot_id in slot_ids:
        slot = Slot.query.get(slot_id)
        if slot and slot.user:
            taken_slots.append(f"{slot.date} {slot.time}")
    if taken_slots:
        flash("Następujące sloty są już zajęte: " + ", ".join(taken_slots), "error")
        return redirect(url_for('battle.battle_detail', battle_id=battle_id))
    
    for slot_id in slot_ids:
        slot = Slot.query.get(slot_id)
        if slot:
            slot.user = username
            slot.units = units
    db.session.commit()
    flash(f'Zapisano na sloty o ID: {slot_ids}', 'success')
    return redirect(url_for('battle.battle_detail', battle_id=battle_id))

@battle_bp.route('/signup_slot/<int:slot_id>', methods=['GET', 'POST'])
@requires_login
def signup_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    if request.method == 'POST':
        username = session.get('username')
        units = request.form.get('units', request.args.get('units', 1))
        try:
            units = int(units)
        except ValueError:
            flash("Ilość jednostek musi być liczbą całkowitą.", "error")
            return redirect(url_for("battle.battle_detail", battle_id=slot.battle_id))
        
        if slot.user:
            flash("Ten slot jest już zajęty.", "error")
            return redirect(url_for("battle.battle_detail", battle_id=slot.battle_id))
        
        slot.user = username
        slot.units = units
        db.session.commit()
        flash("Zapisano slot.", "success")
        return redirect(url_for("battle.battle_detail", battle_id=slot.battle_id))
    
    return render_template("signup_slot.html", slot=slot)

@requires_login
@battle_bp.route('/update_battle_status/<int:battle_id>', methods=['POST'])
def update_battle_status(battle_id):
    data = request.get_json()
    new_status=data.get('status')
    if new_status not in ['active', 'inactive', 'cancelled']:
        logger.error(f"Błąd w przypisaniu statusu: {new_status}")
        return jsonify({"error": "Invalid status"}), 400
    
    battle = Add_battle_db.query.get(battle_id)
    if not battle:
        return jsonify({"error": "Battle not found"}), 404
    
    battle.status = new_status
    db.session.commit()
    logger.info(f"{datetime.now()} | Status bitwy id: >> {battle_id} << został zaktualizowany na {new_status}.")
    return jsonify({"message": "Status został pomyślnie zaktualizowany."}), 200