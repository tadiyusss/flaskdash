from flask import Flask
from flask_mail import Mail
from .extensions import db, login_manager, migrate, socketio
from .route import core, media
from .models.users import User
from .context import init_context
from config import *
from core.initializations.roles import register_default_roles
from core.initializations.extensions import include_all_extensions
from core.initializations.settings import register_default_settings
from core.initializations.commands import register_default_commands

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_context(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail = Mail(app)
    socketio.init_app(app)

    login_manager.login_view = 'core.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(core, url_prefix='/dashboard')
    app.register_blueprint(media)

    with app.app_context():
        db.create_all()
        register_default_roles()
        register_default_settings()
        register_default_commands()
        include_all_extensions(app)
    
    return app, socketio