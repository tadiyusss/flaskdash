from flask import Flask
from .extensions import db, login_manager, migrate
from .route import core
from .models.users import User
from .context import init_context
from config import *
from core.initializations.settings import register_default_settings, register_default_categories
from core.initializations.roles import register_default_roles
from core.initializations.extensions import *
from core.defaults import DEFAULT_SETTINGS

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
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
        register_default_categories()
        register_default_settings()
        register_default_roles()
        register_all_extensions(app)
    
    return app