from flask import render_template
from flask_login import login_required, current_user
from core.utils.decorators import role_required
from core.utils.registry.extensions import EXTENSIONS_METADATA

def generate_routes(core):
    @core.route('/extensions')
    @role_required('Administrator')
    @login_required
    def extensions():
        extensions = EXTENSIONS_METADATA
        return render_template('dashboard/extensions.html', user=current_user, extensions=extensions)