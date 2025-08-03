from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.extensions import db
from core.forms.settings import create_settings_form
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField


def generate_routes(core):
    @core.route('/settings', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def settings():
        form = create_settings_form()

        # Validate the form on submission
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
        
        # Pre-fill the form with existing settings values
        for field in form:
            setting_value = Setting.query.filter_by(key=field.name).first()
            if setting_value:
                if isinstance(field, BooleanField):
                    field.data = setting_value.value == '1'
                else:
                    field.data = setting_value.value
        return render_template('dashboard/settings.html', user=current_user, form = form)