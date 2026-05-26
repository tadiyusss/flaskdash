from typing import List

class SettingItem:
    def __init__(self, key, name, value, field, category_name):
        self.key = key
        self.name = name
        self.value = value
        self.field = field
        self.category_name = category_name
        

class SettingCategory:
    def __init__(self, name, nice_name, description, settings: List[SettingItem]):
        self.name = name
        self.nice_name = nice_name
        self.description = description
        self.settings = settings
