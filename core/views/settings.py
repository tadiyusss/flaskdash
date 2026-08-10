from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from core.extensions import db
from core.forms.settings import create_settings_form
from core.models.settings import Setting
from core.utils.decorators import role_required
from wtforms import BooleanField, FileField
from werkzeug.utils import secure_filename
from core.utils.registry.settings import get_registered_categories
from core.route import core
import uuid
import os

@core.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def settings():
    setting_categories = get_registered_categories()
    forms = [create_settings_form(category) for category in setting_categories]

    for form in forms:
        if form.submit.name in request.form:
            if form.validate_on_submit():
                for field in form:
                    # Skip submit button
                    if field.name == 'submit':
                        continue
                    
                    value = None
                    
                    if isinstance(field, BooleanField):
                        value = '1' if field.data else '0'
                    elif isinstance(field, FileField):

                        if field.data and getattr(field.data, 'filename', ''):
                            if not os.path.exists('media'):
                                os.makedirs('media')
                            
                            filename = secure_filename(field.data.filename)
                            unique_filename = f"{uuid.uuid4().hex}_{filename}"
                            upload_path = os.path.join('media', unique_filename)
                            field.data.save(upload_path)
                            value = unique_filename
                        else:

                            setting = Setting.query.filter_by(key=field.name).first()
                            if setting:
                                value = setting.value
                            continue  
                    else:
                        value = field.data

                    if value is not None:
                        setting = Setting.query.filter_by(key=field.name).first()
                        if setting and setting.value != value:
                            setting.value = value
                            db.session.commit()
                            flash(f"Setting '{setting.name}' updated successfully.", 'global-success')

    for form in forms:
        for field in form:
            if field.name == 'submit':
                continue
                
            setting_value = Setting.query.filter_by(key=field.name).first()
            if setting_value:
                if isinstance(field, BooleanField):
                    field.data = setting_value.value == '1'
                else:
                    field.data = setting_value.value
                    
    return render_template('dashboard/settings.html', user=current_user, forms=forms, categories=setting_categories)