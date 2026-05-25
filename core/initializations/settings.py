from core.models.settings import Setting, SettingCategory, db
from core.defaults import DEFAULT_SETTINGS_CATEGORY
from core.utils.registry.settings import register_setting, register_category

        
def register_default_settings():
    """
    Register default settings to the database and the registry.
    """
    for setting_category in DEFAULT_SETTINGS_CATEGORY:
        register_category(
            name=setting_category.name,
            nice_name=setting_category.nice_name,
            description=setting_category.description
        )

        for setting in setting_category.settings:
            register_setting(
                key=setting.key,
                name=setting.name,
                value=setting.value,
                category_name=setting_category.name,
                field=setting.field
            )