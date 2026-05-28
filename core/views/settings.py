from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from core.extensions import db
from core.forms.settings import create_settings_form
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField
from core.utils.registry.settings import get_registered_categories


def generate_routes(core):
    @core.route('/settings', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def settings():
        setting_categories = get_registered_categories()
        forms = [create_settings_form(category) for category in setting_categories]

        for form in forms:
            if form.validate_on_submit():
                for field in form:
                    print(f"Processing field: {field.name} with data: {field.data}")
                    if isinstance(field, BooleanField):
                        value = '1' if field.data else '0'
                    else:
                        value = field.data

                    setting = Setting.query.filter_by(key=field.name).first()
                    if setting and setting.value != value:
                        setting.value = value
                        db.session.commit()
                        flash(f"Setting '{setting.name}' updated successfully.", 'global-success')

            else:
                print(form.errors)
            
        for form in forms:
            for field in form:
                setting_value = Setting.query.filter_by(key=field.name).first()
                if setting_value:
                    if isinstance(field, BooleanField):
                        field.data = setting_value.value == '1'
                    else:
                        field.data = setting_value.value
        return render_template('dashboard/settings.html', user=current_user, forms=forms, categories=setting_categories)