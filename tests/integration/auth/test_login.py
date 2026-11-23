"""Integration tests for login, logout and session behaviour."""

from __future__ import annotations

import pytest

from core.extensions import db
from core.models.users import LoginHistory, User
from tests.support.constants import DEFAULT_PASSWORD
from tests.support.http import flash_messages


pytestmark = pytest.mark.usefixtures("db_reset")


class TestLoginPage:
    def test_login_page_renders(self, anon_client):
        response = anon_client.get("/dashboard/")
        assert response.status_code == 200
        assert b"Welcome back" in response.data

    def test_login_page_shows_site_title(self, anon_client, app):
        from tests.support import factories

        factories.make_setting(app, "site_title", "Acme Admin")
        assert b"Acme Admin" in anon_client.get("/dashboard/").data

    def test_authenticated_user_is_redirected_away(self, admin_client):
        response = admin_client.get("/dashboard/")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/home")

    def test_root_url_is_not_the_login_page(self, anon_client):
        """The login view lives at ``/dashboard/``; ``/`` is not routed."""
        assert anon_client.get("/").status_code == 404


class TestLoginSuccess:
    def test_valid_credentials_redirect_to_dashboard(self, app, member):
        client = app.test_client()
        response = client.post(
            "/dashboard/", data={"email": member.email, "password": DEFAULT_PASSWORD}
        )

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/home")

    def test_session_is_established(self, app, member):
        client = app.test_client()
        client.post("/dashboard/", data={"email": member.email, "password": DEFAULT_PASSWORD})

        response = client.get("/dashboard/home")
        assert response.status_code == 200

    def test_login_records_history_with_ip(self, app, member):
        client = app.test_client()
        client.post(
            "/dashboard/",
            data={"email": member.email, "password": DEFAULT_PASSWORD},
            environ_base={"REMOTE_ADDR": "203.0.113.7"},
        )

        with app.app_context():
            entry = LoginHistory.query.filter_by(user_id=member.id).one()
            assert entry.ip_address == "203.0.113.7"

    def test_login_is_case_sensitive_on_email(self, app, member):
        client = app.test_client()
        response = client.post(
            "/dashboard/", data={"email": member.email.upper(), "password": DEFAULT_PASSWORD}
        )

        assert response.status_code == 200  # re-rendered form, not a redirect
        assert b"Invalid email or password" in response.data


class TestLoginFailure:
    def test_wrong_password_is_rejected(self, app, member):
        client = app.test_client()
        response = client.post("/dashboard/", data={"email": member.email, "password": "Nope1234!"})

        assert response.status_code == 200
        assert b"Invalid email or password" in response.data
        assert client.get("/dashboard/home").status_code == 302

    def test_unknown_email_is_rejected(self, app):
        client = app.test_client()
        response = client.post("/dashboard/", data={"email": "ghost@example.com", "password": "Nope1234!"})

        assert b"Invalid email or password" in response.data

    def test_failure_message_does_not_reveal_which_field_was_wrong(self, app, member):
        client = app.test_client()
        wrong_password = client.post("/dashboard/", data={"email": member.email, "password": "Nope1234!"})
        unknown_user = client.post("/dashboard/", data={"email": "ghost@example.com", "password": "Nope1234!"})

        assert b"Invalid email or password" in wrong_password.data
        assert b"Invalid email or password" in unknown_user.data

    def test_no_history_recorded_on_failure(self, app, member):
        client = app.test_client()
        client.post("/dashboard/", data={"email": member.email, "password": "Nope1234!"})

        with app.app_context():
            assert LoginHistory.query.count() == 0

    @pytest.mark.parametrize(
        "payload",
        [
            "",
            "not-an-email",
            "' OR 1=1--",
            "admin@example.com'--",
            "' OR '1'='1",
            "admin@example.com' UNION SELECT 1--",
        ],
    )
    def test_sql_injection_payloads_never_authenticate(self, app, admin, payload):
        client = app.test_client()
        response = client.post("/dashboard/", data={"email": payload, "password": "' OR 1=1--"})

        assert response.status_code in (200, 400)
        assert client.get("/dashboard/home").status_code == 302

    def test_missing_fields_flash_label_prefixed_errors(self, anon_client):
        response = anon_client.post("/dashboard/", data={})
        messages = flash_messages(response)
        assert any("Email Address" in message for message in messages)


class TestLogout:
    def test_logout_clears_session(self, admin_client):
        admin_client.get("/dashboard/logout")
        assert admin_client.get("/dashboard/home").status_code == 302

    def test_logout_redirects_to_login(self, admin_client):
        response = admin_client.get("/dashboard/logout")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/")

    def test_logout_without_session_is_harmless(self, anon_client):
        """``@login_required`` bounces anonymous users instead of erroring."""
        response = anon_client.get("/dashboard/logout")
        assert response.status_code == 302

    def test_logout_accepts_get_only(self, admin_client):
        """Destructive GET: no CSRF token can protect it (see security tests)."""
        assert admin_client.post("/dashboard/logout").status_code == 405


class TestDashboardRedirectTarget:
    def test_protected_page_redirects_with_next_parameter(self, anon_client):
        response = anon_client.get("/dashboard/settings")
        assert response.status_code == 302
        assert "next=%2Fdashboard%2Fsettings" in response.headers["Location"]

    def test_next_parameter_is_ignored_on_login(self, app, member):
        """No open redirect: the view always targets ``core.dashboard``."""
        client = app.test_client()
        response = client.post(
            "/dashboard/?next=http://evil.example.com",
            data={"email": member.email, "password": DEFAULT_PASSWORD},
        )

        assert response.status_code == 302
        assert "evil.example.com" not in response.headers["Location"]
        assert response.headers["Location"].endswith("/dashboard/home")


class TestPasswordChangeFlow:
    def test_change_password_with_correct_current(self, app, member_client, member):
        response = member_client.post(
            "/dashboard/profile/edit/password",
            data={"current_password": DEFAULT_PASSWORD, "new_password": "BrandNew1!x"},
        )
        assert response.status_code == 302

        with app.app_context():
            assert db.session.get(User, member.id).check_password("BrandNew1!x")

    def test_change_password_with_wrong_current_is_rejected(self, app, member_client, member):
        member_client.post(
            "/dashboard/profile/edit/password",
            data={"current_password": "WrongOne1!", "new_password": "BrandNew1!x"},
        )

        with app.app_context():
            assert db.session.get(User, member.id).check_password(DEFAULT_PASSWORD)

    def test_new_password_may_violate_registration_policy(self, app, member_client, member):
        """Security finding: the change-password form only enforces length >= 6."""
        response = member_client.post(
            "/dashboard/profile/edit/password",
            data={"current_password": DEFAULT_PASSWORD, "new_password": "aaaaaa"},
        )
        assert response.status_code == 302

        with app.app_context():
            assert db.session.get(User, member.id).check_password("aaaaaa")

    def test_password_change_does_not_log_the_user_out(self, member_client):
        member_client.post(
            "/dashboard/profile/edit/password",
            data={"current_password": DEFAULT_PASSWORD, "new_password": "BrandNew1!x"},
        )
        assert member_client.get("/dashboard/home").status_code == 200
