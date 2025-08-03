from core.models.settings import Setting, SettingCategory, db

_registered_settings = []
_registered_settings_category = []


def register_category(name: str, nice_name: str, description: str = None) -> bool:
    """
    Register a new setting category to the database and the registry.
    """
    exists = SettingCategory.query.filter_by(name=name).first()
    
    if not exists:
        category = SettingCategory(
            name=name,
            nice_name=nice_name,
            description=description
        )
        db.session.add(category)
        db.session.commit()

    _registered_settings_category.append({
        'name': name,
        'nice_name': nice_name,
        'description': description
    })
    return True

def register_setting(key: str, name: str, value: str, category_name: str, field) -> bool:
    """
    Register a new setting to the database and the registry.
    """

    exists = Setting.query.filter_by(key=key).first()
    
    if not exists:
        setting = Setting(
            name=name,
            key=key,
            value=value,
            category_name=category_name,
        )
        db.session.add(setting)
        db.session.commit()

    _registered_settings.append({
        'name': name,
        'key': key,
        'value': value,
        'category_name': category_name,
        'field': field
    })
    return True

def get_registered_settings():
    """
    Get all registered settings.
    """
    return _registered_settings

def get_registered_categories():
    """
    Get all registered setting categories.
    """
    return _registered_settings_category