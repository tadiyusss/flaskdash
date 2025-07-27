from flask import render_template
from flask_login import login_required, current_user
from core.utils.decorators import role_required

def generate_blueprint(core):
    @core.route('/files')
    @role_required('Administrator')
    @login_required
    def files():
        return render_template('dashboard/files.html', user=current_user)