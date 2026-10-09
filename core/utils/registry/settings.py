from core.models.settings import Setting, SettingCategory as SettingCategoryModel
from core.models.settings import db
from core.utils.settings import SettingCategory, SettingItem
from flask import current_app

_registered_settings = []

def register_category(setting_category: SettingCategory) -> bool:
    """
    Register a new setting category to the database and the registry.
    """
    
    exists = SettingCategoryModel.query.filter_by(name=setting_category.name).first()
    current_app.logger.debug(f"Checking if setting category '{setting_category.name}' exists in the database.")

    if not exists:

        current_app.logger.debug(f"Setting category '{setting_category.name}' does not exist. Creating new category.")
        category = SettingCategoryModel(
            name=setting_category.name,
            nice_name=setting_category.nice_name,
            description=setting_category.description
        )
        db.session.add(category)
        db.session.commit()
        current_app.logger.debug(f"Registered setting category: {setting_category.name}")

    for setting in setting_category.settings:
        register_setting(setting)
    
    _registered_settings.append(setting_category)
    current_app.logger.debug(f"Registered setting category: {setting_category.name}")
    return True

def register_setting(setting_item: SettingItem) -> bool:
    """
    Register a new setting to the database and the registry.
    """

    exists = Setting.query.filter_by(key=setting_item.key).first()
    current_app.logger.debug(f"Checking if setting '{setting_item.key}' exists in the database.")


    if not exists:
        current_app.logger.debug(f"Setting '{setting_item.key}' does not exist. Creating new setting.")
        setting = Setting(
            name=setting_item.name,
            key=setting_item.key,
            value=setting_item.value,
            category_name=setting_item.category_name,
        )
        db.session.add(setting)
        db.session.commit()
        current_app.logger.debug(f"Registered setting: {setting_item.key}")

    return True

def get_registered_categories():
    """
    Get all registered setting categories.
    """
    return _registered_settings