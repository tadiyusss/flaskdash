from flask_wtf import FlaskForm
from core.models.settings import Setting
from wtforms import SubmitField
from core.utils.registry.settings import get_registered_settings
from core.utils.settings import SettingCategory

def build_settings_form(category: SettingCategory):
    """
    Dynamically creates a Flask-WTF form from SettingCategory
    """

    class DynamicSettingsForm(FlaskForm):
        submit = SubmitField("Save Settings")
    print(category)
    for setting in category.settings:
        field = setting.field
        field.default = setting.value

        setattr(DynamicSettingsForm, setting.key, field)

    return DynamicSettingsForm()