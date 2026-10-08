import pytest
from core.models.users import User
from core.utils.registry.analytics import get_analytics_items

def test_analytics_mutations(admin_user, normal_user):
    initial_admin_analytics = get_analytics_items(admin_user)
    normal_user_analytics = get_analytics_items(normal_user)
    after_admin_analytics = get_analytics_items(admin_user)

    assert initial_admin_analytics == after_admin_analytics
    assert normal_user_analytics != after_admin_analytics
