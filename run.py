from flask import Flask
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.battle_routes import battle_bp
from routes.admin_routes import admin_bp
from routes.report_routes import report_bp
import security_config
from flask_migrate import Migrate
from security_config import init_csrf
from routes.logistics_routes import logistics_bp
from datetime import datetime

# Import debugowego blueprinta
from debug_code_production.load_db import debug_code_production

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
init_csrf(app)

# WAŻNE: dodajemy wywołanie create_initial_admin()
def create_initial_admin():
    from models.user import User
    from models.role import Role
    from models import db

    with app.app_context():
        if User.query.count() == 0:
            print(f"{datetime.now()}[INIT] Tworzę domyślnego użytkownika: sudo")

            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin')
                db.session.add(admin_role)
                db.session.commit()

            admin_user = User(username='admin')
            admin_user.set_password('admin')
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()

            print("[INIT] Użytkownik sudo został utworzony.")
        else:
            print("[INIT] Użytkownicy już istnieją – pomijam.")

# ⬇️ Tworzenie bazy i użytkownika przy starcie
with app.app_context():
    db.create_all()
    create_initial_admin()  # TO JEST KLUCZOWE

# Rejestracja blueprintów
app.register_blueprint(auth_bp)
app.register_blueprint(battle_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(report_bp)
app.register_blueprint(debug_code_production)
app.register_blueprint(logistics_bp)

# Logowanie
import logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Scheduler slotów
from apscheduler.schedulers.background import BackgroundScheduler
from models.battle import Add_battle_db
from services.slot_service import create_slots_for_battle_shifted

def update_all_battles_slots():
    with app.app_context():
        battles = Add_battle_db.query.all()
        for battle in battles:
            create_slots_for_battle_shifted(battle.id_add_battle_db)
        app.logger.info("Sloty zostały zaktualizowane dla wszystkich bitew.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_battles_slots, trigger='cron', hour=5, minute=0, id='daily_slot_update')
scheduler.start()

if __name__ == "__main__":
    app.run(debug=False, port=5500, host="0.0.0.0")
