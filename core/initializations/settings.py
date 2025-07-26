from core.defaults import DEFAULT_SETTINGS, DEFAULT_SETTINGS_CATEGORY
from core.utils.registry.settings import register_setting, register_choice, register_setting_category

def register_default_categories():
    for category in DEFAULT_SETTINGS_CATEGORY:
        register_setting_category(category['name'], category['nice_name'], category.get('description', ''))

def register_default_settings():
    for setting in DEFAULT_SETTINGS:
        register_setting(setting['name'], setting['key'], setting['value'], setting['type'], setting['category_name'],
                         setting.get('description', ''), setting.get('editable', True))
        if 'choices' in setting:
            for choice in setting['choices']:
                register_choice(setting['key'], choice['value'], choice['label'])