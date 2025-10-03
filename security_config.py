from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def init_csrf(app):
    app.secret_key = 'Suchar88'
    csrf.init_app(app)
