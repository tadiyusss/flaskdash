"""Access-control tests: route coverage, RBAC boundaries and privilege escalation.

The route-inventory test is the safety net for this suite: it fails whenever a
new ``/dashboard`` endpoint is added without an explicit login guard, so an
authorisation regression cannot slip in silently.
"""

from __future__ import annotations

import inspect

import pytest

from core.extensions import db
from core.models.users import User
from core.route import core
from core.views import auth as auth_views
from core.views import extensions as extension_views
from core.views import files as file_views
from core.views import home as home_views
from core.views import profile as profile_views
from core.views import roles as role_views
from core.views import settings as settings_views
from core.views import themes as theme_views
from core.views import users as user_views
from tests.support import factories
from tests.support.constants import PUBLIC_DASHBOARD_ENDPOINTS


pytestmark = pytest.mark.usefixtures("db_reset")

VIEW_MODULES = (
    auth_views,
    extension_views,
    file_views,
    home_views,
    profile_views,
    role_views,
    settings_views,
    theme_views,
    user_views,
)


def dashboard_rules(app):
    return [
        rule
        for rule in app.url_map.iter_rules()
        if rule.rule.startswith("/dashboard") and rule.endpoint != "core.static"
    ]


class TestRouteInventory:
    def test_every_dashboard_route_is_protected(self, app):
        """No ``/dashboard`` view may be reachable without an explicit guard."""
        unguarded = []
        for rule in dashboard_rules(app):
            if rule.endpoint in PUBLIC_DASHBOARD_ENDPOINTS:
                continue
            view = app.view_functions[rule.endpoint]
            source = inspect.getsource(view)
            guarded = (
                "@login_required" in source
                or "role_required" in source
                or "roles_required" in source
                or "developer_mode_required" in source
            )
            if not guarded:
                unguarded.append(f"{rule.rule} ({rule.endpoint})")

        assert not unguarded, f"Routes without an authorisation guard: {unguarded}"

    def test_public_dashboard_endpoints_are_only_the_auth_flow(self, app):
        public = {
            rule.endpoint
            for rule in dashboard_rules(app)
            if rule.endpoint in PUBLIC_DASHBOARD_ENDPOINTS
        }
        assert public <= set(PUBLIC_DASHBOARD_ENDPOINTS)
        assert "core.dashboard" not in public

    def test_no_route_accepts_all_methods_implicitly(self, app):
        """Every rule declares its methods; none default to GET+POST+DELETE..."""
        for rule in dashboard_rules(app):
            assert rule.methods is not None
            assert not {"PUT", "PATCH"} & rule.methods

    def test_destructive_endpoints_use_get(self, app):
        """Documented finding: deletes are reachable with a plain GET.

        Recorded centrally so the full set is visible at a glance and a change
        to POST/POST+CSRF flips exactly this test.
        """
        destructive = {
            "core.delete_user": "GET",
            "core.delete_role": "GET",
            "core.delete_file": "GET",
            "core.logout": "GET",
        }
        by_endpoint = {rule.endpoint: rule for rule in app.url_map.iter_rules() if rule.endpoint in destructive}

        for endpoint, expected in destructive.items():
            assert endpoint in by_endpoint, f"{endpoint} no longer exists"
            assert destructive_methods(by_endpoint[endpoint]) == {expected}


def destructive_methods(rule):
    return {method for method in rule.methods if method not in {"HEAD", "OPTIONS"}}


class TestRoleBoundaries:
    def test_anonymous_cannot_reach_admin_pages(self, anon_client):
        for url in (
            "/dashboard/users",
            "/dashboard/settings",
            "/dashboard/files",
            "/dashboard/users/create",
        ):
            assert anon_client.get(url).status_code in (302, 403), url

    def test_member_cannot_reach_administrator_pages(self, member_client):
        for url in (
            "/dashboard/users",
            "/dashboard/users/create",
            "/dashboard/settings",
            "/dashboard/files",
        ):
            assert member_client.get(url).status_code == 403, url

    def test_editor_role_is_not_administrator(self, app, member):
        """A non-Administrator role grants nothing beyond the member baseline."""
        client = factories_app_client(app, roles=("Editor",))
        assert client.get("/dashboard/users").status_code == 403
        assert client.get("/dashboard/settings").status_code == 403

    def test_profile_views_never_touch_roles(self):
        """No role mutation path exists in ``core.views.profile``."""
        source = inspect.getsource(profile_views)
        assert "set_roles" not in source
        assert "UserRole" not in source

    def test_member_cannot_open_user_management(self, member_client, member):
        assert member_client.get(f"/dashboard/users/manage/{member.uid}").status_code == 403

    def test_roleless_user_gets_baseline_access_only(self, app):
        client = factories_app_client(app, roles=())
        assert client.get("/dashboard/home").status_code == 200
        assert client.get("/dashboard/users").status_code == 403
        assert client.get("/dashboard/settings").status_code == 403

    def test_administrator_role_is_required_not_sufficient_by_name_case(self, app, admin):
        """Role checks are exact-match: ``administrator`` != ``Administrator``."""
        with app.app_context():
            user = db.session.get(User, admin.id)
            assert user.has_role("Administrator") is True
            assert user.has_role("administrator") is False


def factories_app_client(app, roles):
    record = factories.make_user(app, username=f"user-{'-'.join(roles) or 'none'}", roles=roles)
    from tests.support.http import login

    return login(app, record)


class TestPrivilegeEscalation:
    def test_member_cannot_promote_self_through_role_form(self, app, member_client, member):
        with app.app_context():
            from core.models.users import Role

            role_id = Role.query.filter_by(name="Administrator").one().id

        response = member_client.post(
            f"/dashboard/users/manage/{member.uid}",
            data={"role_form": "", f"role_{role_id}": "y"},
        )

        assert response.status_code == 403
        with app.app_context():
            assert db.session.get(User, member.id).has_role("Administrator") is False

    def test_member_cannot_delete_an_administrator(self, app, member_client, admin):
        response = member_client.get(f"/dashboard/users/manage/{admin.uid}/delete")

        assert response.status_code == 403
        with app.app_context():
            assert db.session.get(User, admin.id) is not None

    def test_member_cannot_change_settings_to_open_registration(self, app, member_client):
        member_client.post(
            "/dashboard/settings",
            data={"allow_registration": "y", "site_settings_submit": "Save Changes"},
        )

        assert factories.read_setting(app, "allow_registration") == "0"

    def test_member_cannot_enable_developer_mode(self, app, member_client):
        member_client.post(
            "/dashboard/settings",
            data={"developer_mode": "y", "site_settings_submit": "Save Changes"},
        )

        assert factories.read_setting(app, "developer_mode") == "0"

    def test_member_cannot_access_roles_after_dev_mode_enabled(self, app, member_client):
        factories.make_setting(app, "developer_mode", "1")
        assert member_client.get("/dashboard/roles").status_code == 403

    def test_administrator_can_promote_another_user(self, app, admin_client):
        """Expected admin capability, asserted so it is a deliberate decision."""
        target = factories.make_user(app, username="promote-me", roles=())
        with app.app_context():
            from core.models.users import Role

            role_id = Role.query.filter_by(name="Administrator").one().id

        admin_client.post(
            f"/dashboard/users/manage/{target.uid}",
            data={"role_form": "", f"role_{role_id}": "y"},
        )

        with app.app_context():
            assert db.session.get(User, target.id).has_role("Administrator")


class TestSessionSecurity:
    def test_session_cookie_is_httponly(self, app):
        assert app.config["SESSION_COOKIE_HTTPONLY"] is True

    def test_session_cookie_secure_flag_is_off_by_default(self, app):
        """Finding: cookies are sent over plain HTTP; set SESSION_COOKIE_SECURE in prod."""
        assert app.config.get("SESSION_COOKIE_SECURE") in (None, False)

    def test_samesite_is_not_configured(self, app):
        """Finding: no SameSite policy means cookies ride along on cross-site GETs."""
        assert app.config.get("SESSION_COOKIE_SAMESITE") is None

    def test_stale_user_id_does_not_crash(self, app):
        """A deleted user's session must degrade to anonymous, not 500."""
        record = factories.make_user(app, username="transient")
        from tests.support.http import login

        client = login(app, record)
        with app.app_context():
            db.session.delete(db.session.get(User, record.id))
            db.session.commit()

        assert client.get("/dashboard/home").status_code == 302

    def test_non_numeric_user_id_in_session_causes_500(self, app):
        """Finding: ``load_user`` calls ``int(user_id)`` without a guard.

        A tampered cookie therefore produces a server error instead of being
        rejected -- noisy in logs and useful for reconnaissance.
        """
        client = app.test_client()
        with client.session_transaction() as session:
            session["_user_id"] = "not-a-number"
            session["_fresh"] = True

        assert client.get("/dashboard/home").status_code == 500

    def test_login_refreshes_the_session_identifier(self, app, member):
        """Login should not keep the pre-auth session id (fixation)."""
        client = app.test_client()
        client.get("/dashboard/")
        with client.session_transaction() as session:
            before = session.get("_id")

        client.post("/dashboard/", data={"email": member.email, "password": "Passw0rd!23"})
        with client.session_transaction() as session:
            after = session.get("_id")

        assert before != after
