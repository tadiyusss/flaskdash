from core.models.settings import Setting, SettingCategory as SettingCategoryModel
from core.models.settings import db
from core.utils.settings import SettingCategory, SettingItem

_registered_settings = []

def register_category(setting_category: SettingCategory) -> bool:
    """
    Register a new setting category to the database and the registry.
    """
    
    exists = SettingCategoryModel.query.filter_by(name=setting_category.name).first()
    
    if not exists:
        category = SettingCategoryModel(
            name=setting_category.name,
            nice_name=setting_category.nice_name,
            description=setting_category.description
        )
        db.session.add(category)
        db.session.commit()
    
    _registered_settings.append(setting_category)
    return True

def register_setting(setting_item: SettingItem) -> bool:
    """
    Register a new setting to the database and the registry.
    """

    exists = Setting.query.filter_by(key=setting_item.key).first()
    is_registered = False
    if not exists:
        setting = Setting(
            name=setting_item.name,
            key=setting_item.key,
            value=setting_item.value,
            category_name=setting_item.category_name,
        )
        db.session.add(setting)
        db.session.commit()

    for registered in _registered_settings:
        if registered.name == setting_item.category_name:
            registered.settings.append(setting_item)
            is_registered = True
            break

    if not is_registered:
        raise ValueError(f"Category '{setting_item.category_name}' not found for setting '{setting_item.key}'.")
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
    return _registered_settings