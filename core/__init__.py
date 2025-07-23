from flask import Flask
from .extensions import db, login_manager, migrate
from .views import core
from .models import User
from .context import init_context

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    init_context(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'core.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(core, url_prefix='/dashboard')

    with app.app_context():
        db.create_all()

    return app