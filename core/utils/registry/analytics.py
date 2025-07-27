from core.defaults import DEFAULT_ANALYTICS_ITEMS

analytics_items = DEFAULT_ANALYTICS_ITEMS

def register_default_analytics(title: str, value_function, roles: list):
    analytics_items.append({
        "title": title,
        "value_function": lambda: value_function,
        "roles": roles
    })

def get_analytics_items(current_user):
    return [item for item in analytics_items if current_user.has_role(item['roles'])]