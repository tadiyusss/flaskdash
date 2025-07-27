from flask import render_template
from flask_login import login_required, current_user

def generate_blueprint(core):
    @core.route('/home')
    @login_required
    def dashboard():
        return render_template('dashboard/home.html', user=current_user)