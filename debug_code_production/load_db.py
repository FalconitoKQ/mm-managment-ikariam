from models import battle, bbs, license_token, role, slot, user, zgloszenie
from flask import Flask, blueprints, render_template
from helpers.decorators import requires_login

from models.battle import Add_battle_db
from models.bbs import Bbs
from models.license_token import LicenseToken
from models.role import Role
from models.slot import Slot
from models.user import User
from models.zgloszenie import Zgloszenie

debug_code_production = blueprints.Blueprint('debug_code_production', __name__)

@requires_login
@debug_code_production.route('/debug_production', methods=['GET'])
def read_db():
    # Przykład odczytu danych z bazy danych
    battles = Add_battle_db.query.all()
    bbs_entries = Bbs.query.all()
    license_tokens = LicenseToken.query.all()
    roles = Role.query.all()
    slots = Slot.query.all()
    users = User.query.all()
    zgloszenia = Zgloszenie.query.all()

    # Możesz zwrócić dane w formacie JSON lub renderować szablon
    return render_template('debug_production.html', users=users, battles=battles)
