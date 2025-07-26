from core.models.settings import Setting, SettingsType, SettingChoices, SettingCategory, db

def register_setting_category(name: str, nice_name: str, description: str = None) -> bool:
    exists = SettingCategory.query.filter_by(name=name).first()

    if exists:
        print(f"Setting category '{name}' already exists.")
        return False

    category = SettingCategory(
        name=name,
        nice_name=nice_name,
        description=description
    )
    db.session.add(category)
    db.session.commit()
    print(f"Setting category '{name}' registered successfully.")
    return True

def register_setting(name: str, key: str, value: str, type: SettingsType, category_name: str, description: str = None, editable: bool = True) -> bool:
    exists = Setting.query.filter_by(key=key).first()

    if type not in SettingsType:
        raise ValueError(f"Invalid setting type: {type}")
    
    if exists:
        print(f"Setting with key '{key}' already exists.")
        return False

    setting = Setting(
        name=name,
        key=key,
        value=value,
        type=type,
        description=description,
        editable=editable,
        category_name=category_name
    )
    db.session.add(setting)
    db.session.commit()
    print(f"Setting '{name}' registered successfully.")
    return True
    
def get_setting(key: str) -> Setting | bool:
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        raise False
    return setting

def update_setting(key: str, value: str) -> bool:
    setting = Setting.query.filter_by(key=key).first()

    if not setting:
        return False

    setting.value = value
    db.session.commit()
    return True

def register_choice(setting_key: int, value: str, label: str) -> bool:
    exists = SettingChoices.query.filter_by(setting_key=setting_key, value=value).first()

    if exists:
        print(f"Choice with value '{value}' for setting '{setting_key}' already exists.")
        return False
    
    choice = SettingChoices(
        setting_key=setting_key,
        value=value,
        label=label
    )
    db.session.add(choice)
    db.session.commit()
    print(f"Choice '{label}' registered successfully for setting '{setting_key}'.")
    return True