from core.utils.registry.analytics import get_analytics_items

def snapshot(grids):
    return [(grid.title, [card.title for card in grid.contents]) for grid in grids]

def test_analytics_mutations(admin_user, normal_user):
    initial_admin_analytics = snapshot(get_analytics_items(admin_user))
    normal_user_analytics = snapshot(get_analytics_items(normal_user))
    after_admin_analytics = snapshot(get_analytics_items(admin_user))

    assert initial_admin_analytics
    assert initial_admin_analytics == after_admin_analytics
    assert normal_user_analytics == []