from core.defaults import DEFAULT_ANALYTICS_GRID
from core.utils.analytics import Grid
from core.models.users import User

_analytics_grids = list(DEFAULT_ANALYTICS_GRID)

def register_analytics(grid: Grid):
    _analytics_grids.append(grid)
    
def register_analytics_item(item, grid_title):
    for grid in _analytics_grids:
        if grid.title == grid_title:
            grid.contents.append(item)
            break

def get_analytics_items(user: User):
    """
    Get analytics items for the current user based on their roles.
    This function checks the registered analytics grids and filters the items based on the user's roles.
    """

    items = []
    for grid in _analytics_grids:
        if not grid.show_for_user(user):
            continue

        visible_contents = grid.filter_contents_for_user(user)
        if visible_contents:
            items.append(Grid(
                roles=grid.roles,
                columns=grid.columns_count,
                rows=grid.rows_count,
                title=grid.title,
                contents=visible_contents,
            ))
    return items