from core.defaults import DEFAULT_SIDEBAR_ITEMS

_registered_sidebar_items = list(DEFAULT_SIDEBAR_ITEMS)  

def register_sidebar_item(item: dict):
    _registered_sidebar_items.append(item)

def get_sidebar_items_for_user(user):
    def has_role(roles):
        return user.role in roles or '*' in roles

    return [
        {
            "name": category['name'],
            "items": [item for item in category['items'] if has_role(item['roles'])]
        }
        for category in _registered_sidebar_items
        if has_role(category['roles']) and any(has_role(item['roles']) for item in category['items'])
    ]
