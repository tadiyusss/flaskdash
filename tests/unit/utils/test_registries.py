"""Unit tests for the settings, sidebar, theme and extension registries.

``g.settings`` is populated by the app's ``before_request`` hook, so anything
that reads it (the sidebar registry) must run inside a request context with the
dict primed -- ``settings_context`` does exactly that, using the same source
the hook uses.
"""

from __future__ import annotations

from contextlib import contextmanager

import pytest
from flask import g

from core.extensions import db
from core.models.settings import Setting
from core.models.users import User
from core.utils.registry import analytics as analytics_registry
from core.utils.registry import side_navigation, themes
from core.utils.registry.settings import get_registered_categories
from core.utils.settings import SettingCategory, SettingItem
from tests.support import factories


pytestmark = pytest.mark.usefixtures("db_reset")


@contextmanager
def settings_context(app):
    """Request context with ``g.settings`` primed exactly like ``before_request``."""
    with app.test_request_context():
        g.settings = {setting.key: setting.value for setting in Setting.query.all()}
        yield


def sidebar_titles(app, record):
    with settings_context(app):
        categories = side_navigation.get_sidebar_items_for_user(db.session.get(User, record.id))
        return [item.name for category in categories for item in category.items]


class TestSettingsRegistry:
    def test_default_category_is_registered(self):
        names = [category.name for category in get_registered_categories()]
        assert "site_settings" in names

    def test_registry_accumulates_on_every_create_app(self, app):
        """Regression: ``register_category`` always appends to the global list.

        ``create_app`` therefore duplicates the category on every call, which
        makes ``/dashboard/settings`` render one extra card per app instance
        built in the process (visible as duplicate form submits).
        """
        before = len(get_registered_categories())
        from core import create_app
        from config import TestingConfig

        create_app(TestingConfig)
        assert len(get_registered_categories()) == before + 1

    def test_setting_item_carries_metadata(self):
        item = SettingItem(
            key="demo_key",
            name="Demo",
            value="x",
            field=object(),
            category_name="site_settings",
        )
        assert item.key == "demo_key"
        assert item.category_name == "site_settings"

    def test_category_holds_its_items(self):
        item = SettingItem(key="k", name="N", value=None, field=object(), category_name="c")
        category = SettingCategory(name="c", nice_name="C", description="d", settings=[item])
        assert category.settings == [item]

    def test_register_category_creates_missing_rows(self, app):
        from core.utils.registry.settings import register_category

        item = SettingItem(
            key="extra_flag", name="Extra Flag", value="1", field=object(), category_name="extra"
        )
        category = SettingCategory(name="extra", nice_name="Extra", description="d", settings=[item])

        with app.app_context():
            assert register_category(category) is True
            assert Setting.query.filter_by(key="extra_flag").first() is not None

    def test_register_category_does_not_duplicate_rows(self, app):
        from core.utils.registry.settings import register_category

        item = SettingItem(
            key="stable_key", name="Stable", value="1", field=object(), category_name="stable"
        )
        category = SettingCategory(name="stable", nice_name="Stable", description="d", settings=[item])

        with app.app_context():
            register_category(category)
            register_category(category)
            assert Setting.query.filter_by(key="stable_key").count() == 1


class TestSidebarRegistry:
    def test_admin_sees_administrative_entries(self, app, admin):
        titles = sidebar_titles(app, admin)
        assert {"Users", "Settings", "Files"} <= set(titles)

    def test_regular_user_sees_only_personal_entries(self, app, member):
        titles = sidebar_titles(app, member)
        assert {"Home", "Profile", "Logout"} <= set(titles)
        assert not {"Users", "Settings", "Files", "Roles"} & set(titles)

    def test_developer_entries_hidden_when_developer_mode_off(self, app, admin):
        factories.make_setting(app, "developer_mode", "0")
        titles = sidebar_titles(app, admin)

        assert "Roles" not in titles
        assert "Themes" not in titles
        assert "Extensions" not in titles

    def test_developer_entries_visible_when_developer_mode_on(self, app, admin):
        factories.make_setting(app, "developer_mode", "1")
        titles = sidebar_titles(app, admin)

        assert {"Roles", "Themes", "Extensions"} <= set(titles)

    def test_categories_without_visible_items_are_dropped(self, app):
        record = factories.make_user(app, username="nothing", roles=())
        with settings_context(app):
            categories = side_navigation.get_sidebar_items_for_user(db.session.get(User, record.id))

        assert all(category.items for category in categories)

    def test_register_sidebar_item_requires_existing_category(self, app):
        from core.utils.dashboard import DashboardItem

        item = DashboardItem(name="X", icon_type="svg", icon="", route="core.dashboard", roles=["*"])
        with app.app_context():
            with pytest.raises(ValueError):
                side_navigation.register_sidebar_item(item, "Does Not Exist")

    def test_register_sidebar_item_appends_to_category(self, app):
        from core.utils.dashboard import DashboardItem

        item = DashboardItem(name="Injected", icon_type="svg", icon="", route="core.dashboard", roles=["*"])
        with app.app_context():
            before = len(side_navigation._registered_sidebar_items[0].items)
            side_navigation.register_sidebar_item(item, "Dashboard")
            after = len(side_navigation._registered_sidebar_items[0].items)

        assert after == before + 1

    def test_missing_developer_mode_setting_raises_keyerror(self, app, admin):
        """Regression: ``g.settings['developer_mode']`` is indexed directly.

        Deleting or renaming the setting makes every dashboard page return 500
        instead of degrading gracefully.
        """
        factories.delete_setting(app, "developer_mode")
        with settings_context(app):
            with pytest.raises(KeyError):
                side_navigation.get_sidebar_items_for_user(db.session.get(User, admin.id))


class TestThemeRegistry:
    def test_default_theme_is_discovered(self, app):
        with app.app_context():
            names = [theme.name for theme in themes.get_all_themes()]
        assert "default" in names

    def test_theme_exposes_metadata(self, app):
        with app.app_context():
            default = next(t for t in themes.get_all_themes() if t.name == "default")
            info = default.info()
        assert isinstance(info, dict)
        assert info

    def test_theme_is_valid_when_files_exist(self, app):
        with app.app_context():
            default = next(t for t in themes.get_all_themes() if t.name == "default")
            assert default.is_valid is True

    def test_invalid_theme_is_rejected(self, app, tmp_path):
        from core.utils.themes import Theme

        broken = tmp_path / "broken"
        broken.mkdir()
        with app.app_context():
            assert themes.register_theme(Theme(name="broken", path=broken)) is False

    def test_duplicate_registration_is_not_detected(self, app):
        """Regression: the guard compares ``theme.path`` against Theme objects.

        ``register_theme`` checks ``theme.path in _registered_themes`` while the
        list holds ``Theme`` instances, so the membership test never matches and
        the same theme is appended every time.  Asserted as-is so a fix flips
        this test.
        """
        with app.app_context():
            existing = themes.get_all_themes()[0]
            before = len(themes._registered_themes)
            assert themes.register_theme(existing) is True
            assert len(themes._registered_themes) == before + 1

    def test_missing_tailwind_binary_raises(self, app, monkeypatch):
        """Building a theme shells out; a missing CLI surfaces FileNotFoundError."""
        import subprocess

        def boom(*args, **kwargs):
            raise FileNotFoundError("tailwindcss: not found")

        monkeypatch.setattr(subprocess, "run", boom)
        with app.app_context():
            with pytest.raises(FileNotFoundError):
                themes.get_all_themes()


class TestAnalyticsRegistry:
    def test_default_grid_present(self):
        titles = [grid.title for grid in analytics_registry._analytics_grids]
        assert "Dashboard Analytics" in titles

    def test_register_analytics_item_ignores_unknown_grid(self, app):
        from core.utils.analytics import MediumAnalyticsCardData

        card = MediumAnalyticsCardData(title="Orphan", value_function=lambda: 1)
        with app.app_context():
            analytics_registry.register_analytics_item(card, "Nonexistent Grid")

        titles = [
            content.title for grid in analytics_registry._analytics_grids for content in grid.contents
        ]
        assert "Orphan" not in titles

    def test_register_analytics_item_appends_to_grid(self, app):
        from core.utils.analytics import MediumAnalyticsCardData

        card = MediumAnalyticsCardData(title="Injected", value_function=lambda: 1)
        with app.app_context():
            analytics_registry.register_analytics_item(card, "Dashboard Analytics")

        titles = [content.title for content in analytics_registry._analytics_grids[0].contents]
        assert "Injected" in titles
