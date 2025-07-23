from flask import g, current_app
from core.models import Setting

def init_context(app):

    
    @app.before_request
    def before_request():
        g.settings = {}
        for setting in Setting.query.all():
            g.settings[setting.key] = setting.value