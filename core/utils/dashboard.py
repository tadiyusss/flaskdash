from core.models.users import Role

class DashboardItem:
    def __init__(self, name: str, icon_type: str, icon: str, route: str, roles: list[Role] = None):
        self.name = name
        self.icon_type = icon_type
        self.icon = icon
        self.route = route
        self.roles = roles or []

    def is_role_allowed(self, roles: list[str]) -> bool:
        if '*' in self.roles:
            return True
        for role in roles:
            if role.role.name in self.roles:
                return True
        return False


class DashboardCategory:
    def __init__(self, name: str, roles: list[Role] = None, items: list[DashboardItem] = None):
        self.name = name
        self.roles = roles or []
        self.items = items or []

    def is_role_allowed(self, roles: list[str]) -> bool:
        if '*' in self.roles:
            return True
        for role in roles:
            if role.role.name in self.roles:
                return True
        return False