"""Unit tests for the analytics data structures and role filtering."""

from __future__ import annotations

import pytest

from core.extensions import db
from core.models.users import User
from core.utils.analytics import (
    Grid,
    LargeAnalyticsCardData,
    MediumAnalyticsCardData,
    SmallAnalyticsCardData,
)
from core.utils.analytics_functions import (
    get_active_users,
    get_total_users,
    get_uploads_storage_usage,
)
from core.utils.registry.analytics import get_analytics_items
from tests.support import factories


pytestmark = pytest.mark.usefixtures("db_reset")

CARD = MediumAnalyticsCardData(title="Card", value_function=lambda: 1)


def _grid(roles, cards):
    return Grid(title="Grid", roles=roles, columns=4, contents=cards)


class TestCardVisibility:
    def test_card_without_roles_is_visible_to_everyone(self, app, member):
        with app.app_context():
            user = db.session.get(User, member.id)
            assert CARD.show_for_user(user) is True

    def test_card_restricted_to_matching_role(self, app, admin):
        card = MediumAnalyticsCardData(title="Admin", value_function=lambda: 1, roles=["Administrator"])
        with app.app_context():
            assert card.show_for_user(db.session.get(User, admin.id)) is True

    def test_card_hidden_from_other_roles(self, app, member):
        card = MediumAnalyticsCardData(title="Admin", value_function=lambda: 1, roles=["Administrator"])
        with app.app_context():
            assert card.show_for_user(db.session.get(User, member.id)) is False

    def test_card_with_resource_roles_shows_to_that_role(self, app, member):
        card = MediumAnalyticsCardData(title="U", value_function=lambda: 1, roles=["User"])
        with app.app_context():
            assert card.show_for_user(db.session.get(User, member.id)) is True


class TestGridVisibility:
    def test_grid_without_roles_is_hidden(self, app, member):
        with app.app_context():
            assert _grid(None, [CARD]).show_for_user(db.session.get(User, member.id)) is False

    def test_wildcard_grid_is_visible(self, app, member):
        with app.app_context():
            assert _grid(["*"], [CARD]).show_for_user(db.session.get(User, member.id)) is True

    def test_grid_with_matching_role_is_visible(self, app, member):
        with app.app_context():
            assert _grid(["User"], [CARD]).show_for_user(db.session.get(User, member.id)) is True

    def test_grid_with_non_matching_role_is_hidden(self, app, member):
        with app.app_context():
            assert _grid(["Administrator"], [CARD]).show_for_user(db.session.get(User, member.id)) is False

    def test_filter_contents_drops_unauthorised_cards(self, app, member):
        public = MediumAnalyticsCardData(title="Public", value_function=lambda: 1)
        restricted = MediumAnalyticsCardData(title="Restricted", value_function=lambda: 1, roles=["Administrator"])
        with app.app_context():
            titles = [
                card.title
                for card in _grid(["*"], [public, restricted]).filter_contents_for_user(
                    db.session.get(User, member.id)
                )
            ]

        assert titles == ["Public"]

    def test_filter_contents_keeps_authorised_cards(self, app, admin):
        cards = [
            MediumAnalyticsCardData(title="A", value_function=lambda: 1),
            MediumAnalyticsCardData(title="B", value_function=lambda: 1, roles=["Administrator"]),
        ]
        with app.app_context():
            titles = [
                card.title
                for card in _grid(["*"], cards).filter_contents_for_user(db.session.get(User, admin.id))
            ]

        assert titles == ["A", "B"]


class TestResponsiveSpans:
    @pytest.mark.parametrize(
        ("columns", "expected"),
        [
            (1, {"sm": 1, "md": 1, "lg": 1, "xl": 1, "default": 1}),
            (2, {"sm": 1, "md": 1, "lg": 1, "xl": 2, "default": 1}),
            (4, {"sm": 1, "md": 2, "lg": 3, "xl": 4, "default": 1}),
            (8, {"sm": 5, "md": 6, "lg": 7, "xl": 8, "default": 1}),
        ],
    )
    def test_spans_clamp_to_one(self, columns, expected):
        assert Grid(columns=columns).calculate_responsive_spans() == expected

    def test_zero_columns_is_clamped(self):
        spans = Grid(columns=0).calculate_responsive_spans()
        assert set(spans.values()) == {1}


class TestSerialisation:
    def test_medium_card_dict(self):
        payload = MediumAnalyticsCardData(
            title="T", value_function=lambda: 1, subtitle="S", icon="<svg/>", roles=["User"]
        ).to_dict()
        assert payload["type"] == "MediumAnalyticsCardData"
        assert payload["subtitle"] == "S"
        assert payload["rows"] if "rows" in payload else True

    def test_large_card_dict_has_progress_fields(self):
        payload = LargeAnalyticsCardData(
            title="T", value_function=lambda: 1, subtitle="S", increase=5, progress=0.5
        ).to_dict()
        assert payload["increase"] == 5
        assert payload["progress"] == 0.5
        assert payload["type"] == "LargeAnalyticsCardData"

    def test_small_card_dict_has_icon_only(self):
        payload = SmallAnalyticsCardData(title="T", value_function=lambda: 1, icon="<svg/>").to_dict()
        assert payload["icon"] == "<svg/>"
        assert "subtitle" not in payload

    def test_grid_dict_serialises_contents(self):
        payload = _grid(["*"], [CARD]).to_dict()
        assert payload["columns"] == 4
        assert payload["contents"][0]["title"] == "Card"


class TestRegistryFiltering:
    def test_administrator_receives_default_grid(self, app, admin):
        with app.app_context():
            grids = get_analytics_items(db.session.get(User, admin.id))

        titles = [card.title for grid in grids for card in grid.contents]
        assert titles == ["Total Users", "Active Users", "Uploads Storage Usage"]

    def test_regular_user_receives_nothing(self, app, member):
        with app.app_context():
            assert get_analytics_items(db.session.get(User, member.id)) == []

    def test_roleless_user_receives_nothing(self, app):
        record = factories.make_user(app, username="noanalytics", roles=())
        with app.app_context():
            assert get_analytics_items(db.session.get(User, record.id)) == []

    def test_each_call_returns_a_new_grid_instance(self, app, admin):
        """The registry must not be mutated by rendering."""
        with app.app_context():
            first = get_analytics_items(db.session.get(User, admin.id))
            second = get_analytics_items(db.session.get(User, admin.id))

        assert first is not second
        assert first[0] is not second[0]
        assert len(first[0].contents) == len(second[0].contents)


class TestAnalyticsFunctions:
    def test_total_users_counts_rows(self, app):
        factories.make_user(app, username="count1")
        factories.make_user(app, username="count2")
        with app.app_context():
            assert get_total_users() == 2

    def test_active_users_is_zero_without_logins(self, app, member):
        with app.app_context():
            assert get_active_users() == 0

    def test_active_users_counts_distinct_users(self, app, member):
        factories.make_login_history(app, member.id)
        with app.app_context():
            assert get_active_users() == 1

    def test_storage_usage_reports_a_unit(self, app):
        assert get_uploads_storage_usage().endswith(("B", "KB", "MB", "GB", "TB"))

    def test_storage_usage_scans_relative_uploads_directory(self, app, storage):
        """``get_uploads_storage_usage`` walks ``core/static/uploads`` relative to CWD."""
        payload = b"0123456789"
        upload = storage.parent / "core" / "static" / "uploads"
        (upload / "usage.bin").write_bytes(payload)

        assert get_uploads_storage_usage() == "10.00 B"

    def test_storage_usage_is_zero_when_directory_missing(self, app, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert get_uploads_storage_usage() == "0.00 B"
