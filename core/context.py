from flask import g, current_app
from core.models import Setting
from core.utils.registry.side_navigation import get_sidebar_items_for_user
from flask_login import current_user

def init_context(app):

    @app.before_request
    def before_request():
        g.settings = {}
        for setting in Setting.query.all():
            g.settings[setting.key] = setting.value

    @app.context_processor
    def inject_sidebar_items():
        return dict(get_sidebar=lambda: get_sidebar_items_for_user(current_user))