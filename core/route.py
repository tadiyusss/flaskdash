from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .extensions import db
from .forms import * 
from core.views import auth, users, profile, roles, settings, extensions, files, home
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

auth.generate_blueprint(core)
users.generate_blueprint(core)
profile.generate_blueprint(core)
roles.generate_blueprint(core)
settings.generate_blueprint(core)
extensions.generate_blueprint(core)
files.generate_blueprint(core)
home.generate_blueprint(core)





