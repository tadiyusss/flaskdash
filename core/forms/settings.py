from flask_wtf import FlaskForm
from core.styles import Style
from core.models.settings import Setting
from core.utils.registry.settings import get_registered_settings
style = Style()

def create_settings_form():
    class DynamicSettingsForm(FlaskForm):
        pass
    
    for setting in get_registered_settings():
        field = setting['field']
        existing_setting = Setting.query.filter_by(key=setting['key']).first()
        if existing_setting and existing_setting.value is not None:
            field.data = existing_setting.value        
        setattr(DynamicSettingsForm, setting['key'], field)
    return DynamicSettingsForm()