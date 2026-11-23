"""Integration tests for ``/dashboard/settings``, roles, themes and extensions."""

from __future__ import annotations

import io

import pytest

from core.extensions import db
from core.models.settings import Setting
from core.models.users import Role
from tests.support import factories
from tests.support.constants import PNG_BYTES


pytestmark = pytest.mark.usefixtures("db_reset")

SETTINGS_PAYLOAD = {
    "site_title": "Acme",
    "site_description": "Acme admin panel",
    "site_theme": "default",
    "default_user_role": "User",
    "site_settings_submit": "Save Changes",
}


class TestSettingsPage:
    def test_renders_for_administrator(self, admin_client):
        assert admin_client.get("/dashboard/settings").status_code == 200

    def test_renders_every_default_setting_field(self, admin_client):
        body = admin_client.get("/dashboard/settings").get_data(as_text=True)
        for key in (
            "site_title",
            "favicon_icon",
            "website_logo",
            "site_description",
            "site_theme",
            "allow_registration",
            "allow_first_name_last_name",
            "default_user_role",
            "developer_mode",
        ):
            assert f'name="{key}"' in body, key

    def test_member_is_forbidden(self, member_client):
        assert member_client.get("/dashboard/settings").status_code == 403

    def test_member_cannot_write_settings(self, app, member_client):
        member_client.post("/dashboard/settings", data=SETTINGS_PAYLOAD)

        assert factories.read_setting(app, "site_title") == "FlaskDash"

    def test_renders_one_card_per_registered_category(self, admin_client):
        body = admin_client.get("/dashboard/settings").get_data(as_text=True)
        assert body.count("site_settings_submit") >= 1


class TestSettingsWrite:
    def test_text_setting_is_saved(self, app, admin_client):
        admin_client.post("/dashboard/settings", data=SETTINGS_PAYLOAD)

        assert factories.read_setting(app, "site_title") == "Acme"
        assert factories.read_setting(app, "site_description") == "Acme admin panel"

    def test_change_is_visible_on_the_next_request(self, app, admin_client):
        admin_client.post("/dashboard/settings", data={**SETTINGS_PAYLOAD, "site_title": "Renamed"})

        assert b"Renamed" in admin_client.get("/dashboard/home").data

    def test_boolean_enabled_is_stored_as_one(self, app, admin_client):
        admin_client.post("/dashboard/settings", data={**SETTINGS_PAYLOAD, "allow_registration": "y"})

        assert factories.read_setting(app, "allow_registration") == "1"

    def test_boolean_absent_is_stored_as_zero(self, app, admin_client):
        factories.make_setting(app, "allow_registration", "1")
        admin_client.post("/dashboard/settings", data=SETTINGS_PAYLOAD)

        assert factories.read_setting(app, "allow_registration") == "0"

    def test_invalid_select_value_is_rejected(self, app, admin_client):
        admin_client.post("/dashboard/settings", data={**SETTINGS_PAYLOAD, "site_theme": "../../etc"})

        assert factories.read_setting(app, "site_theme") == "default"

    def test_over_long_title_is_rejected(self, app, admin_client):
        admin_client.post("/dashboard/settings", data={**SETTINGS_PAYLOAD, "site_title": "x" * 101})

        assert factories.read_setting(app, "site_title") == "FlaskDash"

    def test_missing_required_field_blocks_the_whole_form(self, app, admin_client):
        admin_client.post("/dashboard/settings", data={"site_settings_submit": "Save Changes"})

        assert factories.read_setting(app, "site_title") == "FlaskDash"

    def test_file_upload_replaces_setting_value(self, app, admin_client, storage):
        response = admin_client.post(
            "/dashboard/settings",
            data={**SETTINGS_PAYLOAD, "website_logo": (io.BytesIO(PNG_BYTES), "logo.png")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        stored = factories.read_setting(app, "website_logo")
        assert stored and stored.endswith("logo.png")
        assert (storage / stored).is_file()

    def test_invalid_file_extension_is_rejected(self, app, admin_client, storage):
        admin_client.post(
            "/dashboard/settings",
            data={**SETTINGS_PAYLOAD, "website_logo": (io.BytesIO(b"MZ"), "payload.exe")},
            content_type="multipart/form-data",
        )

        assert factories.read_setting(app, "website_logo") == ""

    def test_replacing_a_file_deletes_the_previous_one(self, app, admin_client, storage):
        admin_client.post(
            "/dashboard/settings",
            data={**SETTINGS_PAYLOAD, "website_logo": (io.BytesIO(PNG_BYTES), "first.png")},
            content_type="multipart/form-data",
        )
        first = factories.read_setting(app, "website_logo")

        admin_client.post(
            "/dashboard/settings",
            data={**SETTINGS_PAYLOAD, "website_logo": (io.BytesIO(PNG_BYTES), "second.png")},
            content_type="multipart/form-data",
        )
        second = factories.read_setting(app, "website_logo")

        assert first != second
        assert not (storage / first).exists()

    def test_theme_setting_drives_the_stylesheet_link(self, app, anon_client):
        """``base.html`` builds the stylesheet URL from ``g.settings['site_theme']``."""
        factories.make_setting(app, "site_theme", "default")
        body = anon_client.get("/dashboard/").get_data(as_text=True)
        assert "themes/default.css" in body

    def test_unsafe_theme_value_breaks_the_page(self, app, anon_client):
        """Regression: the theme value is interpolated straight into the URL.

        Nothing validates ``site_theme`` at render time, so a value that is not
        a real theme file yields a broken stylesheet link (and a missing CSS on
        the login page); with a traversal-ish value the rendered markup changes
        shape.  Only the settings form (select choices) keeps this sane.
        """
        factories.make_setting(app, "site_theme", "does-not-exist")
        response = anon_client.get("/dashboard/")

        assert response.status_code == 200
        assert "themes/does-not-exist.css" in response.get_data(as_text=True)


class TestRolesPage:
    @pytest.fixture(autouse=True)
    def _developer_mode(self, db_reset):
        factories.make_setting(db_reset, "developer_mode", "1")

    def test_renders_for_administrator(self, admin_client):
        assert admin_client.get("/dashboard/roles").status_code == 200

    def test_lists_default_roles(self, admin_client):
        body = admin_client.get("/dashboard/roles").get_data(as_text=True)
        for role in ("Administrator", "Editor", "User"):
            assert role in body

    def test_create_role(self, app, admin_client):
        response = admin_client.post(
            "/dashboard/roles", data={"name": "Auditor", "description": "Read only access"}
        )

        assert response.status_code == 302
        with app.app_context():
            assert Role.query.filter_by(name="Auditor").first() is not None

    def test_duplicate_role_name_rejected(self, app, admin_client):
        response = admin_client.post(
            "/dashboard/roles", data={"name": "Administrator", "description": "Dup"}
        )

        assert response.status_code == 200
        with app.app_context():
            assert Role.query.filter_by(name="Administrator").count() == 1

    def test_blank_role_rejected(self, app, admin_client):
        admin_client.post("/dashboard/roles", data={"name": "", "description": ""})

        with app.app_context():
            assert Role.query.count() == 3

    def test_default_role_cannot_be_deleted(self, app, admin_client):
        with app.app_context():
            uid = Role.query.filter_by(name="User").one().uid

        response = admin_client.get(f"/dashboard/roles/{uid}/delete")

        assert response.status_code == 302
        with app.app_context():
            assert Role.query.filter_by(name="User").first() is not None

    def test_custom_role_can_be_deleted(self, app, admin_client):
        uid = factories.make_role(app, "Temporary")

        admin_client.get(f"/dashboard/roles/{uid}/delete")

        with app.app_context():
            assert Role.query.filter_by(name="Temporary").first() is None

    def test_deleting_unknown_role_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/roles/ghost/delete").status_code == 404

    def test_member_is_forbidden(self, member_client):
        assert member_client.get("/dashboard/roles").status_code == 403

    def test_blocked_when_developer_mode_off(self, app, admin_client):
        factories.make_setting(app, "developer_mode", "0")
        assert admin_client.get("/dashboard/roles").status_code == 403


class TestThemesPage:
    @pytest.fixture(autouse=True)
    def _developer_mode(self, db_reset):
        factories.make_setting(db_reset, "developer_mode", "1")

    def test_renders_for_administrator(self, admin_client):
        assert admin_client.get("/dashboard/themes").status_code == 200

    def test_lists_default_theme(self, admin_client):
        assert b"default" in admin_client.get("/dashboard/themes").data

    def test_view_known_theme(self, admin_client):
        assert admin_client.get("/dashboard/themes/view/default").status_code == 200

    def test_view_unknown_theme_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/themes/view/nope").status_code == 404

    def test_member_is_forbidden(self, member_client):
        assert member_client.get("/dashboard/themes").status_code == 403


class TestExtensionsPage:
    @pytest.fixture(autouse=True)
    def _developer_mode(self, db_reset):
        factories.make_setting(db_reset, "developer_mode", "1")

    def test_renders_for_administrator(self, admin_client):
        assert admin_client.get("/dashboard/extensions").status_code == 200

    def test_managing_a_missing_extension_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/extensions/manage/ghost").status_code == 404

    def test_member_is_forbidden(self, member_client):
        assert member_client.get("/dashboard/extensions").status_code == 403


class TestSettingsDoubleSubmit:
    def test_two_categories_render_once_each(self, app, admin_client):
        """Guards against duplicate cards from a growing settings registry.

        ``create_app`` appends to the module-level registry on every call, so a
        process that builds the app more than once renders duplicate forms.
        This pins the current session-scoped count.
        """
        body = admin_client.get("/dashboard/settings").get_data(as_text=True)
        assert body.count('name="site_settings_submit"') == 1
