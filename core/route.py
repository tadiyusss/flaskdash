from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .extensions import db
from .forms import * 
import uuid, os
from werkzeug.utils import secure_filename
from core.views import auth, users

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

auth.generate_blueprint(core)
users.generate_blueprint(core)

@core.route('/extensions')
@login_required
def extensions():
    return render_template('dashboard/extensions.html', user=current_user)

@core.route('/home')
@login_required
def dashboard():
    return render_template('dashboard/home.html', user=current_user)

@core.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = create_settings_form()

    if form.validate_on_submit():
        for field in form:
            setting = Setting.query.filter_by(key=field.name).first()
            if setting:
                setting.value = field.data
                db.session.commit()
        flash('Settings updated successfully.', 'global-success')
        return redirect(url_for('core.settings'))
    return render_template('dashboard/settings.html', user=current_user, form = form)



