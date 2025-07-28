from flask import render_template
from flask_login import login_required, current_user
from core.utils.decorators import role_required

def generate_routes(core):
    @core.route('/extensions')
    @role_required('Administrator')
    @login_required
    def extensions():
        return render_template('dashboard/extensions.html', user=current_user)