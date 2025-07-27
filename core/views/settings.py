from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.extensions import db
from core.forms.settings import create_settings_form
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField

def generate_blueprint(core):
    @core.route('/settings', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def settings():
        form = create_settings_form()

        if form.validate_on_submit():
            for field in form:
                if isinstance(field, BooleanField):
                    value = '1' if field.data else '0'
                else:
                    value = field.data

                setting = Setting.query.filter_by(key=field.name).first()
                if setting and setting.value != value:
                    setting.value = value
                    db.session.commit()
                    flash(f"Setting '{setting.name}' updated successfully.", 'global-success')
            return redirect(url_for('core.settings'))
        return render_template('dashboard/settings.html', user=current_user, form = form)