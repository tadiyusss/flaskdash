from core.models.settings import Setting, SettingCategory, db
from core.defaults import DEFAULT_SETTINGS, DEFAULT_SETTINGS_CATEGORY
from core.utils.registry.settings import register_setting, register_category

def register_default_categories():
    for category in DEFAULT_SETTINGS_CATEGORY:
        register_category(
            name=category['name'],
            nice_name=category['nice_name'],
            description=category.get('description', '')
        )
        
def register_default_settings():
    """
    Register default settings to the database and the registry.
    """
    for setting in DEFAULT_SETTINGS:
        register_setting(
            key=setting['key'],
            name=setting['name'],
            value=setting['value'],
            category_name=setting['category_name'],
            field=setting['field']
        )