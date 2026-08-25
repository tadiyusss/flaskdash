from flask import Blueprint

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')
media = Blueprint('media', __name__)
system = Blueprint('system', __name__)

