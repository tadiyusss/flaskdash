from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .extensions import db
from .forms import * 
from core.views import auth, users, profile, roles, settings, extensions, files, home
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

auth.generate_routes(core)
users.generate_routes(core)
profile.generate_routes(core)
roles.generate_routes(core)
settings.generate_routes(core)
extensions.generate_routes(core)
files.generate_routes(core)
home.generate_routes(core)





