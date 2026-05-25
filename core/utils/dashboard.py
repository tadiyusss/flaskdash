

class DashboardItem:
    def __init__(self, name: str, icon_type: str, icon: str, route: str, roles: list[str] = None):
        self.name = name
        self.icon_type = icon_type
        self.icon = icon
        self.route = route
        self.roles = roles or []

    def is_role_allowed(self, role: str) -> bool:
        return role in self.roles or '*' in self.roles


class DashboardCategory:
    def __init__(self, name: str, roles: list[str] = None, items: list[DashboardItem] = None):
        self.name = name
        self.roles = roles or []
        self.items = items or []

    def is_role_allowed(self, role: str) -> bool:
        return role in self.roles or '*' in self.roles
    