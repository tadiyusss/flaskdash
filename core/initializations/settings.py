from core.defaults import DEFAULT_SETTINGS
from core.utils.registry.settings import register_setting, register_choice

def register_default_settings():
    for setting in DEFAULT_SETTINGS:
        register_setting(setting['name'], setting['key'], setting['value'], setting['type'], 
                         setting.get('description', ''), setting.get('editable', True))
        if 'choices' in setting:
            for choice in setting['choices']:
                register_choice(setting['key'], choice['value'], choice['label'])