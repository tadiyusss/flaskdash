from flask_wtf import FlaskForm
from core.models.settings import Setting
from core.models.settings import SettingCategory as SettingCategoryModel
from core.utils.registry.settings import get_registered_settings
from core.utils.settings import SettingCategory, SettingItem
from core.extensions import db

def create_settings_form(category: SettingCategory):
    """
    Create a dynamic WTForms form based on the registered settings for a given category.
    :param category: The settings category for which to create the form.
    :return: A dynamically generated WTForms form class.
    """

    class DynamicSettingsForm(FlaskForm):
        pass

    for setting in category.settings:
        field = setting.field
        existing_setting = Setting.query.filter_by(key=setting.key).first()
        if existing_setting:
            field.default = existing_setting.value
        else:

                new_setting = Setting(
                    key=setting.key,
                    name=setting.name,
                    value=setting.value,
                    category=SettingCategoryModel.query.filter_by(name=category.name).first()
                )
                db.session.add(new_setting)
                db.session.commit()
                field.default = setting.value

        setattr(DynamicSettingsForm, setting.key, field)

    return DynamicSettingsForm()