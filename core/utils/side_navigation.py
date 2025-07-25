from core.defaults import DEFAULT_SIDEBAR_ITEMS

_registered_sidebar_items = list(DEFAULT_SIDEBAR_ITEMS)  

def register_sidebar_item(item: dict):
    _registered_sidebar_items.append(item)

def get_sidebar_items_for_user(user):
    def user_has_role(item):
        if not item.get('roles'):
            return True
        if '*' in item['roles']:
            return True
        if user.is_authenticated and user.role in item['roles']:
            return True
        return False
    return [item for item in _registered_sidebar_items if user_has_role(item)]

