from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .extensions import db
from .forms import * 
from core.views import auth, users
from core.forms.settings import create_settings_form
from core.models import Setting
from core.utils.decorators import role_required
from core.utils.side_navigation import register_sidebar_item

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

auth.generate_blueprint(core)
users.generate_blueprint(core)


@core.route('/extensions')
@role_required('Administrator')
@login_required
def extensions():

    return render_template('dashboard/extensions.html', user=current_user)

@core.route('/home')
@login_required
def dashboard():
    return render_template('dashboard/home.html', user=current_user)

@core.route('/settings', methods=['GET', 'POST'])
@role_required('Administrator')
@login_required
def settings():
    form = create_settings_form()

    if form.validate_on_submit():
        for field in form:
            setting = Setting.query.filter_by(key=field.name).first()
            if setting:
                if field.data != setting.value:
                    flash(f'Setting {setting.name} updated.', 'global-success')
                    setting.value = field.data
                db.session.commit()
        return redirect(url_for('core.settings'))
    return render_template('dashboard/settings.html', user=current_user, form = form)



