from core.defaults import DEFAULT_SIDEBAR_ITEMS

_registered_sidebar_items = list(DEFAULT_SIDEBAR_ITEMS)  

def register_category(name: str, roles: list):
    """
    Register a new category in the sidebar.
    :param name: The name of the category.
    :param roles: A list of roles that can access this category.
    :param items: A list of items belonging to this category.
    """
    category = {
        "name": name,
        "roles": roles,
        "items": []
    }
    _registered_sidebar_items.append(category)

def register_sidebar_item(name: str, icon_type: str, icon: str, route: str, roles: list, category_name: str):
    """
    Register a new item in the sidebar.
    :param name: The name of the item.
    :param icon_type: The type of icon (e.g., 'svg', 'url').
    :param icon: The icon content or URL.
    :param route: The route for the item.
    :param roles: A list of roles that can access this item.
    :param category_name: The name of the category this item belongs to.
    """
    if not any(category['name'] == category_name for category in _registered_sidebar_items):
        raise ValueError("Category name does not exist. Please register the category first.")

    item = {
        "name": name,
        "icon_type": icon_type,
        "icon": icon,
        "route": route,
        "roles": roles
    }

    for category in _registered_sidebar_items:
        if category['name'] == category_name:
            category['items'].append(item)

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
