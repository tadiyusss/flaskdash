from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, IntegerField, URLField, BooleanField, SelectField
from core.styles import Style
from core.models.settings import Setting, SettingChoices, SettingsType

style = Style()

def create_settings_form():
    class DynamicSettingsForm(FlaskForm):
        pass

    settings = Setting.query.all()
    for setting in settings:
        field_type = setting.type.value
        if field_type == 'text':
            field = StringField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'bool':
            field = BooleanField(setting.name,
                description=setting.description,
                default=True if setting.value.lower() == '1' else False,
            )

        elif field_type == 'textarea':
            field = TextAreaField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.textarea},
                
            )
        elif field_type =='number':
            field = IntegerField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'email':
            field = EmailField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'url':
            field = URLField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'datetime':
            field = StringField(setting.name,
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.text_input}
            )
        elif field_type == 'select':
            choices = SettingChoices.query.filter_by(setting_key=setting.key).all()
            field = SelectField(setting.name,
                choices=[(choice.value, choice.label) for choice in choices],
                default=setting.value,
                description=setting.description,
                render_kw={"class": style.select}
            )
        else:
            continue
        setattr(DynamicSettingsForm, setting.key, field)
    return DynamicSettingsForm()