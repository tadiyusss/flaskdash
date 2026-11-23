"""Integration tests for dashboard pages, RBAC and the user-management flow."""

from __future__ import annotations

import pytest

from core.extensions import db
from core.models.users import Role, User, UserRole
from tests.support import factories
from tests.support.constants import DEFAULT_PASSWORD
from tests.support.http import flash_messages, login


pytestmark = pytest.mark.usefixtures("db_reset")


ADMIN_PAGES = ("/dashboard/home", "/dashboard/users", "/dashboard/settings", "/dashboard/profile", "/dashboard/files")
MEMBER_PAGES = ("/dashboard/home", "/dashboard/profile")


LOGIN_REDIRECT_PAGES = (
    "/dashboard/home",
    "/dashboard/settings",
    "/dashboard/profile",
    "/dashboard/files",
    "/dashboard/themes",
)

ROLE_GUARDED_PAGES = (
    "/dashboard/users",
    "/dashboard/users/create",
    "/dashboard/roles",
    "/dashboard/extensions",
)


class TestAnonymousAccess:
    @pytest.mark.parametrize("url", LOGIN_REDIRECT_PAGES)
    def test_login_only_pages_redirect_to_login(self, anon_client, url):
        response = anon_client.get(url)
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/dashboard/?next=")

    @pytest.mark.parametrize("url", ROLE_GUARDED_PAGES)
    def test_role_guarded_pages_return_403_to_anonymous_users(self, anon_client, url):
        """Regression: decorator order makes these 403 instead of a login redirect.

        ``@role_required(...)`` sits above ``@login_required``, so it runs
        first and aborts with 403 for anonymous visitors.  Two consequences:
        the UX is inconsistent with the rest of the dashboard, and the response
        discloses that the route exists.  Asserted as-is so a fix flips it.
        """
        response = anon_client.get(url)
        assert response.status_code == 403

    def test_static_assets_are_public(self, anon_client):
        """Expected: CSS/JS must load on the login page itself."""
        assert anon_client.get("/dashboard/static/css/global.css").status_code == 200


class TestAdministratorAccess:
    @pytest.mark.parametrize("url", ADMIN_PAGES)
    def test_administrator_reaches_admin_pages(self, admin_client, url):
        assert admin_client.get(url).status_code == 200

    def test_dashboard_shows_analytics(self, admin_client):
        body = admin_client.get("/dashboard/home").get_data(as_text=True)
        assert "Total Users" in body
        assert "Active Users" in body
        assert "Uploads Storage Usage" in body

    def test_dashboard_counts_users(self, app, admin_client, admin):
        factories.make_user(app, username="second")
        body = admin_client.get("/dashboard/home").get_data(as_text=True)
        assert "Total Users" in body


class TestMemberAccess:
    @pytest.mark.parametrize("url", MEMBER_PAGES)
    def test_member_reaches_personal_pages(self, member_client, url):
        assert member_client.get(url).status_code == 200

    @pytest.mark.parametrize(
        "url",
        ["/dashboard/users", "/dashboard/users/create", "/dashboard/settings", "/dashboard/files"],
    )
    def test_member_is_forbidden_from_admin_pages(self, member_client, url):
        assert member_client.get(url).status_code == 403

    def test_member_dashboard_hides_analytics(self, member_client):
        body = member_client.get("/dashboard/home").get_data(as_text=True)
        assert "Total Users" not in body

    def test_member_sidebar_hides_admin_links(self, member_client):
        body = member_client.get("/dashboard/home").get_data(as_text=True)
        assert "/dashboard/users" not in body
        assert "/dashboard/settings" not in body


class TestDeveloperModeGate:
    @pytest.mark.parametrize(
        "url", ["/dashboard/roles", "/dashboard/themes", "/dashboard/extensions"]
    )
    def test_admin_is_blocked_when_developer_mode_off(self, app, admin_client, url):
        factories.make_setting(app, "developer_mode", "0")
        assert admin_client.get(url).status_code == 403

    @pytest.mark.parametrize(
        "url", ["/dashboard/roles", "/dashboard/themes", "/dashboard/extensions"]
    )
    def test_admin_reaches_page_when_developer_mode_on(self, app, admin_client, url):
        factories.make_setting(app, "developer_mode", "1")
        assert admin_client.get(url).status_code == 200

    def test_member_still_blocked_when_developer_mode_on(self, app, member_client, url=None):
        factories.make_setting(app, "developer_mode", "1")
        assert member_client.get("/dashboard/roles").status_code == 403


class TestUserListing:
    def test_list_excludes_the_current_user(self, app, admin_client, admin):
        factories.make_user(app, username="someone-else")

        body = admin_client.get("/dashboard/users").get_data(as_text=True)
        assert "someone-else" in body
        assert f">{admin.username}<" not in body

    def test_empty_state_is_rendered(self, admin_client):
        assert "No users found" in admin_client.get("/dashboard/users").get_data(as_text=True)

    def test_user_rows_are_html_escaped(self, app, admin_client):
        factories.make_user(app, username="<script>alert(1)</script>")

        body = admin_client.get("/dashboard/users").get_data(as_text=True)
        assert "<script>alert(1)</script>" not in body
        assert "&lt;script&gt;" in body


class TestCreateUser:
    def _payload(self, **overrides):
        data = {
            "username": "created",
            "email": "created@example.com",
            "password": DEFAULT_PASSWORD,
            "firstname": "Cre",
            "lastname": "Ated",
            "role": "Editor",
        }
        data.update(overrides)
        return data

    @pytest.fixture(autouse=True)
    def _names_enabled(self, db_reset):
        factories.make_setting(db_reset, "allow_first_name_last_name", "1")

    def test_form_renders(self, admin_client):
        assert admin_client.get("/dashboard/users/create").status_code == 200

    def test_creates_user_with_selected_role(self, app, admin_client):
        response = admin_client.post("/dashboard/users/create", data=self._payload())

        assert response.status_code == 302
        with app.app_context():
            user = User.query.filter_by(username="created").one()
            assert [link.role.name for link in user.user_roles] == ["Editor"]
            assert user.check_password(DEFAULT_PASSWORD)

    def test_duplicate_username_rejected(self, app, admin_client, member):
        response = admin_client.post(
            "/dashboard/users/create", data=self._payload(username=member.username)
        )

        assert response.status_code == 200
        with app.app_context():
            assert User.query.filter_by(username=member.username).count() == 1

    def test_duplicate_email_rejected(self, app, admin_client, member):
        response = admin_client.post(
            "/dashboard/users/create", data=self._payload(email=member.email)
        )

        assert response.status_code == 200
        with app.app_context():
            assert User.query.filter_by(email=member.email).count() == 1

    def test_weak_password_rejected(self, app, admin_client):
        admin_client.post(
            "/dashboard/users/create",
            data=self._payload(password="weak", retype_password="weak"),
        )

        with app.app_context():
            assert User.query.filter_by(username="created").first() is None

    def test_unknown_role_is_rejected_by_the_select_field(self, app, admin_client):
        """The role select validates against the DB-derived choice list."""
        response = admin_client.post(
            "/dashboard/users/create", data=self._payload(role="Ghost Role")
        )

        assert response.status_code == 200
        with app.app_context():
            assert User.query.filter_by(username="created").first() is None

    def test_role_is_required(self, app, admin_client):
        payload = self._payload()
        payload.pop("role")

        response = admin_client.post("/dashboard/users/create", data=payload)

        assert response.status_code == 200
        with app.app_context():
            assert User.query.filter_by(username="created").first() is None

    def test_member_cannot_create_users(self, app, member_client):
        member_client.post("/dashboard/users/create", data=self._payload())

        with app.app_context():
            assert User.query.filter_by(username="created").first() is None


class TestManageUser:
    def _other(self, app):
        return factories.make_user(app, username="target")

    def test_manage_page_renders(self, app, admin_client):
        target = self._other(app)
        assert admin_client.get(f"/dashboard/users/manage/{target.uid}").status_code == 200

    def test_managing_self_redirects(self, app, admin_client, admin):
        response = admin_client.get(f"/dashboard/users/manage/{admin.uid}")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/users")

    def test_unknown_uid_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/users/manage/does-not-exist").status_code == 404

    def test_name_update_persists(self, app, admin_client):
        target = self._other(app)
        response = admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"name_form": "", "username": "renamed", "email": "renamed@example.com"},
        )

        assert response.status_code == 302
        with app.app_context():
            assert db.session.get(User, target.id).username == "renamed"

    def test_name_update_rejects_duplicate_username(self, app, admin_client, member):
        target = self._other(app)
        admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"name_form": "", "username": member.username, "email": target.email},
        )

        with app.app_context():
            assert db.session.get(User, target.id).username == "target"

    def test_password_update_persists(self, app, admin_client):
        target = self._other(app)
        admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"password_form": "", "new_password": "Fresh1Pass!"},
        )

        with app.app_context():
            assert db.session.get(User, target.id).check_password("Fresh1Pass!")

    def test_short_password_is_rejected(self, app, admin_client):
        target = self._other(app)
        admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"password_form": "", "new_password": "abc"},
        )

        with app.app_context():
            assert db.session.get(User, target.id).check_password(DEFAULT_PASSWORD)

    def test_role_update_grants_administrator(self, app, admin_client):
        """Known weakness: any administrator can promote any account."""
        target = self._other(app)
        with app.app_context():
            role_id = Role.query.filter_by(name="Administrator").one().id

        admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"role_form": "", f"role_{role_id}": "y"},
        )

        with app.app_context():
            assert db.session.get(User, target.id).has_role("Administrator")

    def test_role_update_revokes_roles(self, app, admin_client):
        target = self._other(app)
        admin_client.post(f"/dashboard/users/manage/{target.uid}", data={"role_form": ""})

        with app.app_context():
            assert db.session.get(User, target.id).user_roles == []

    def test_empty_profile_image_upload_flashes_error(self, app, admin_client):
        target = self._other(app)
        response = admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"edit_profile_form": ""},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestDeleteUser:
    def test_delete_removes_user(self, app, admin_client):
        target = factories.make_user(app, username="doomed")
        admin_client.get(f"/dashboard/users/manage/{target.uid}/delete")

        with app.app_context():
            assert db.session.get(User, target.id) is None

    def test_delete_self_is_blocked(self, app, admin_client, admin):
        admin_client.get(f"/dashboard/users/manage/{admin.uid}/delete")

        with app.app_context():
            assert db.session.get(User, admin.id) is not None

    def test_delete_unknown_user_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/users/manage/nope/delete").status_code == 404

    def test_delete_cleans_up_roles_and_history(self, app, admin_client):
        target = factories.make_user(app, username="history-owner")
        factories.make_login_history(app, target.id)

        admin_client.get(f"/dashboard/users/manage/{target.uid}/delete")

        with app.app_context():
            assert UserRole.query.filter_by(user_id=target.id).count() == 0

    def test_member_cannot_delete_users(self, app, member_client):
        target = factories.make_user(app, username="safe")
        assert member_client.get(f"/dashboard/users/manage/{target.uid}/delete").status_code == 403

        with app.app_context():
            assert db.session.get(User, target.id) is not None


class TestProfilePage:
    def test_profile_renders_for_member(self, member_client):
        assert member_client.get("/dashboard/profile").status_code == 200

    def test_name_change_persists(self, app, member_client, member):
        member_client.post(
            "/dashboard/profile/edit/name",
            data={"username": "newname", "email": "new@example.com", "submit": "Save Changes"},
        )

        with app.app_context():
            user = db.session.get(User, member.id)
            assert user.username == "newname"
            assert user.email == "new@example.com"

    def test_duplicate_username_is_rejected(self, app, member_client, member):
        other = factories.make_user(app, username="occupied")
        member_client.post(
            "/dashboard/profile/edit/name",
            data={"username": other.username, "email": member.email, "submit": "Save Changes"},
        )

        with app.app_context():
            assert db.session.get(User, member.id).username == member.username

    def test_duplicate_email_is_rejected(self, app, member_client, member):
        other = factories.make_user(app, username="owner", email="owner@example.com")
        member_client.post(
            "/dashboard/profile/edit/name",
            data={"username": member.username, "email": other.email, "submit": "Save Changes"},
        )

        with app.app_context():
            assert db.session.get(User, member.id).email == member.email

    def test_member_cannot_change_another_user(self, app, member_client, admin):
        """The profile view only ever mutates ``current_user``."""
        member_client.post(
            "/dashboard/profile/edit/name",
            data={"username": "renamed-admin", "email": admin.email, "submit": "Save Changes"},
        )

        with app.app_context():
            assert db.session.get(User, admin.id).username == admin.username

    def test_profile_get_does_not_accept_post(self, member_client):
        assert member_client.post("/dashboard/profile").status_code == 405


class TestMissingSettings:
    """Templates index ``g.settings`` directly, so a missing key breaks pages."""

    def test_missing_site_theme_breaks_the_login_page(self, app, anon_client):
        factories.delete_setting(app, "site_theme")
        assert anon_client.get("/dashboard/").status_code == 500

    def test_missing_developer_mode_breaks_the_dashboard(self, app, admin_client):
        factories.delete_setting(app, "developer_mode")
        assert admin_client.get("/dashboard/home").status_code == 500

    def test_missing_favicon_is_tolerated(self, app, anon_client):
        factories.delete_setting(app, "favicon_icon")
        assert anon_client.get("/dashboard/").status_code == 200
