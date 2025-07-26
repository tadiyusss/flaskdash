from flask import Flask
from .extensions import db, login_manager, migrate
from .route import core
from .models import User
from .context import init_context
from config import *
from core.utils.registry.settings import register_setting, register_choice
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
        for setting in DEFAULT_SETTINGS:
            register_setting(
                name=setting['name'],
                key=setting['key'],
                value=setting['value'],
                type=setting['type'],
                description=setting.get('description'),
                editable=setting.get('editable', True)
            )
            if 'choices' in setting:
                for choice in setting['choices']:
                    register_choice(
                        setting_key=setting['key'],
                        value=choice['value'],
                        label=choice['label']
                    )

    return app