from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from core.extensions import db
from core.forms.settings import build_settings_form
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField
from core.utils.registry.settings import get_registered_categories, get_registered_settings


def generate_routes(core):
    @core.route('/settings', methods=['GET', 'POST'])
    @role_required('Administrator')
    @login_required
    def settings():
        registered_settings_categories = get_registered_categories()
        registered_settings = get_registered_settings()

        for category in registered_settings_categories:
            forms = [build_settings_form(category) for category in registered_settings_categories]
        
        for form in forms:
            for field in form:
                setting_value = Setting.query.filter_by(key=field.name).first()
                if setting_value:
                    if isinstance(field, BooleanField):
                        field.data = setting_value.value == '1'
                    else:
                        field.data = setting_value.value
        return render_template('dashboard/settings.html', user=current_user, form = form, registered_settings_categories=registered_settings_categories, registered_settings=registered_settings)