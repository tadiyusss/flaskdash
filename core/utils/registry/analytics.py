from core.defaults import DEFAULT_ANALYTICS_GRID
from core.utils.analytics import Grid

_default_analytics_grid = DEFAULT_ANALYTICS_GRID

def register_analytics(grid: Grid):
    _default_analytics_grid.append(grid)
    
def get_analytics_items(user):
    """
    Get analytics items for the current user based on their roles.
    This function checks the registered analytics grids and filters the items based on the user's roles.
    """

    items = []
    for grid in _default_analytics_grid:
        if grid.show_for_user(user):
            grid.filter_contents_for_user(user)
            if len(grid.contents) > 0:
                items.append(grid)


    return items