from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .extensions import db
from .forms import * 

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')
media = Blueprint('media', __name__)

from core.views import auth, users, profile, roles, settings, extensions, files, home
from core.views import media as media_views

