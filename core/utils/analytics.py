from typing import List, Union
from core.models.users import User

"""
Cards Naming Guide:

- For small cards, use `SmallAnalyticsCardData`
- For medium cards, use `MediumAnalyticsCardData`
- For large cards, use `LargeAnalyticsCardData`

"""

class GlobalCardData:
    def __init__(self, title: str, value_function: callable, roles: List[str] = None, colspan=1, rowspan=1):
        self.title = title
        self.value_function = value_function
        self.roles = roles or []
        self.colspan = colspan
        self.rowspan = rowspan


    def to_dict(self):
        return {
            'title': self.title,
            'value_function': self.value_function,
            'roles': self.roles,
            'colspan': self.colspan,
            'rowspan': self.rowspan,
            'type': self.__class__.__name__
        }

    def show_for_user(self, user): 
        if not self.roles: 
            return True 
        return any(user.has_role(role) for role in self.roles)
        

class LargeAnalyticsCardData(GlobalCardData):

    def __init__(self, title: str, value_function: callable, subtitle=None, icon=None, increase=None, progress=None, roles=None):
        super().__init__(title, value_function, roles=roles, colspan=1, rowspan=1)
        self.subtitle = subtitle
        self.icon = icon
        self.increase = increase
        self.progress = progress


    def to_dict(self):
        data = super().to_dict()
        data.update({
            'subtitle': self.subtitle,
            'icon': self.icon,
            'increase': self.increase,
            'progress': self.progress,
        })
        return data

class MediumAnalyticsCardData(GlobalCardData):

    def __init__(self, title: str, value_function: callable, subtitle=None, icon=None, roles=None):
        super().__init__(title, value_function, roles=roles, colspan=1, rowspan=1)
        self.subtitle = subtitle
        self.icon = icon

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'subtitle': self.subtitle,
            'icon': self.icon
        })
        return data

class SmallAnalyticsCardData(GlobalCardData):
    def __init__(self, title: str, value_function: callable, roles=None, icon=None):
        super().__init__(title, value_function, roles=roles, colspan=1, rowspan=1)
        self.icon = icon

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'icon': self.icon
        })
        return data

class Grid:
    def __init__(self, roles: List[str] = None, columns: int = 4, rows: int = 1, title: str = None, contents: List[Union[
        GlobalCardData, 
        LargeAnalyticsCardData, 
        MediumAnalyticsCardData, 
        SmallAnalyticsCardData
    ]] = None):
        self.roles = roles
        self.columns_count = columns
        self.rows_count = rows
        self.title = title
        self.contents = contents or []

    def to_dict(self):
        return {
            'columns': self.columns_count,
            'rows': self.rows_count,
            'title': self.title,
            'roles': self.roles,
            'contents': [content.to_dict() for content in self.contents]
        }

    def show_for_user(self, user: User):
        if not self.roles:
            return False

        for role in self.roles:
            if user.has_role(role):
                return True
        return False
    
    def filter_contents_for_user(self, user):
        filtered_contents = []

        for content in self.contents:
            if content.show_for_user(user):
                filtered_contents.append(content)
        self.contents = filtered_contents

    def calculate_responsive_spans(self):

        def clamp(value):
            return max(1, value)

        xl = clamp(self.columns_count)
        lg = clamp(xl - 1)
        md = clamp(lg - 1)
        sm = clamp(md - 1)

        return {
            "sm": sm,
            "md": md,
            "lg": lg,
            "xl": xl,
            "default": 1
        }