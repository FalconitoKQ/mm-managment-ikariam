# services/slot_service.py
from datetime import datetime, timedelta
from models import db
from models.slot import Slot

def create_slots_for_day(battle_id, target_date):
    """Tworzy sloty co 15 minut dla danej daty i bitwy."""
    times = [f"{hour:02d}:{minute:02d}"
             for hour in range(24)
             for minute in [0, 15, 30, 45]]
    new_slots = []
    for t in times:
        new_slot = Slot(date=target_date, time=t, user=None, units=None, battle_id=battle_id)
        new_slots.append(new_slot)
    db.session.bulk_save_objects(new_slots)
    db.session.commit()

def create_slots_for_battle_shifted(battle_id):
    """
    Sprawdza i tworzy brakujące sloty dla bitwy na dni w zakresie:
    wczoraj, dziś, jutro i pojutrze.
    Jeśli sloty dla danej daty już istnieją, nie są nadpisywane.
    """
    today = datetime.now().date()
    date_range = [today + timedelta(days=offset) for offset in range(-1, 3)]  # -1, 0, +1, +2
    for day in date_range:
        # Jeśli przynajmniej jeden slot istnieje, pomijamy tworzenie slotów dla tej daty
        slot_exists = Slot.query.filter_by(battle_id=battle_id, date=day).first()
        if not slot_exists:
            create_slots_for_day(battle_id, day)
