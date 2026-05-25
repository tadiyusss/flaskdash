from core.models.settings import Setting, db
from core.models.settings import SettingCategory as SettingCategoryModel
from core.utils.settings import SettingCategory

_registered_settings = []
_registered_settings_category = []


def register_category(category: SettingCategory) -> bool:
    """
    Register a new setting category to the database and the registry.
    """
    exists = SettingCategoryModel.query.filter_by(name=category.name).first()
    
    if not exists:
        category = SettingCategoryModel(
            name=category.name,
            nice_name=category.nice_name,
            description=category.description
        )
        db.session.add(category)
        db.session.commit()

    _registered_settings_category.append(category)
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