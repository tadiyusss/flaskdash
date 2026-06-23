from core.defaults import DEFAULT_SIDEBAR_ITEMS
from core.utils.dashboard import DashboardCategory, DashboardItem
from core.models.users import User

_registered_sidebar_items = list(DEFAULT_SIDEBAR_ITEMS)  

def register_category(category: DashboardCategory):
    """
    Register a new category in the sidebar.
    :param name: The name of the category.
    :param roles: A list of roles that can access this category.
    :param items: A list of items belonging to this category.
    """
    _registered_sidebar_items.append(category)

def register_sidebar_item(item: DashboardItem, category_name: str):
    """
    Register a new item in the sidebar.
    :param item: The dashboard item to register.
    :param category_name: The name of the category this item belongs to.
    """

    if not any(category.name == category_name for category in _registered_sidebar_items):
        raise ValueError("Category name does not exist. Please register the category first.")

    for category in _registered_sidebar_items:
        if category.name == category_name:
            category.items.append(item)

def get_sidebar_items_for_user(user: User):
    """
    Get the sidebar items that should be visible to a user based on their role.
    This function checks the registered sidebar items and filters them based on the user's roles.
    Category will only be included if it has at least one item that the user can access.

    :param user: The user object for whom to retrieve the sidebar items.
    """

    visible_sidebar = []
    for category in _registered_sidebar_items:
        if category.is_role_allowed(user.user_roles):
            visible_items = []
            for item in category.items:
                if item.is_role_allowed(user.user_roles):
                    visible_items.append(item)
            if visible_items:
                category = DashboardCategory(name=category.name, roles=category.roles, items=visible_items)
                visible_sidebar.append(category)
    return visible_sidebar