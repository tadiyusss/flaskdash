from core.defaults import DEFAULT_SETTINGS_CATEGORY
from core.utils.registry.settings import register_setting, register_category

        
def register_default_settings():
    """
    Register default settings to the database and the registry.
    """
    for setting_category in DEFAULT_SETTINGS_CATEGORY:
        register_category(setting_category)