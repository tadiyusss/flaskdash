"""Integration tests for registration, password reset and the settings gates."""

from __future__ import annotations

import pytest

from core.extensions import db
from core.models.users import User
from core.utils.tokens import generate_reset_token
from tests.support import factories
from tests.support.constants import ALT_PASSWORD, DEFAULT_PASSWORD
from tests.support.http import flash_messages


pytestmark = pytest.mark.usefixtures("db_reset")


def register_payload(**overrides):
    data = {
        "firstname": "Ada",
        "lastname": "Lovelace",
        "username": "ada",
        "email": "ada@example.com",
        "password": DEFAULT_PASSWORD,
        "retype_password": DEFAULT_PASSWORD,
    }
    data.update(overrides)
    return data


class TestRegistrationDisabled:
    """``allow_registration`` defaults to ``0``, so sign-up is closed."""

    def test_get_redirects_to_login(self, anon_client):
        response = anon_client.get("/dashboard/register")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/")

    def test_post_does_not_create_a_user(self, app, anon_client):
        anon_client.post("/dashboard/register", data=register_payload())

        with app.app_context():
            assert User.query.count() == 0

    def test_flashes_disabled_message(self, anon_client):
        response = anon_client.get("/dashboard/register", follow_redirects=True)
        assert b"registration is disabled" in response.data


class TestRegistrationEnabled:
    @pytest.fixture(autouse=True)
    def _open_registration(self, db_reset):
        """Must depend on ``db_reset`` so settings survive the table reset."""
        factories.make_setting(db_reset, "allow_registration", "1")
        factories.make_setting(db_reset, "allow_first_name_last_name", "1")

    def test_form_renders(self, anon_client):
        response = anon_client.get("/dashboard/register")
        assert response.status_code == 200
        assert b"Create your account" in response.data

    def test_successful_registration_logs_user_in(self, app, anon_client):
        response = anon_client.post("/dashboard/register", data=register_payload())

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/home")
        assert anon_client.get("/dashboard/home").status_code == 200

    def test_new_user_gets_default_role(self, app, anon_client):
        anon_client.post("/dashboard/register", data=register_payload())

        with app.app_context():
            user = User.query.filter_by(username="ada").one()
            assert [link.role.name for link in user.user_roles] == ["User"]

    def test_new_user_does_not_get_administrator(self, app, anon_client):
        anon_client.post("/dashboard/register", data=register_payload())

        with app.app_context():
            user = User.query.filter_by(username="ada").one()
            assert user.has_role("Administrator") is False

    def test_password_is_hashed(self, app, anon_client):
        anon_client.post("/dashboard/register", data=register_payload())

        with app.app_context():
            user = User.query.filter_by(username="ada").one()
            assert user.password != DEFAULT_PASSWORD
            assert user.check_password(DEFAULT_PASSWORD)

    def test_duplicate_email_is_rejected(self, app, anon_client, member):
        response = anon_client.post(
            "/dashboard/register", data=register_payload(email=member.email)
        )

        assert b"Email already exists" in response.data
        with app.app_context():
            assert User.query.count() == 1

    def test_duplicate_username_is_rejected(self, app, anon_client, member):
        response = anon_client.post(
            "/dashboard/register", data=register_payload(username=member.username)
        )

        assert b"Username already exists" in response.data
        with app.app_context():
            assert User.query.count() == 1

    def test_mismatched_passwords_are_rejected(self, app, anon_client):
        response = anon_client.post(
            "/dashboard/register",
            data=register_payload(password=DEFAULT_PASSWORD, retype_password="Different1!"),
        )

        assert b"Passwords do not match" in response.data
        with app.app_context():
            assert User.query.count() == 0

    def test_weak_password_is_rejected(self, app, anon_client):
        response = anon_client.post(
            "/dashboard/register", data=register_payload(password="weak", retype_password="weak")
        )

        assert b"password" in response.data.lower()
        with app.app_context():
            assert User.query.count() == 0

    def test_first_name_fields_are_rendered(self, anon_client):
        assert b'name="firstname"' in anon_client.get("/dashboard/register").data

    def test_authenticated_user_is_redirected_away(self, admin_client):
        response = admin_client.get("/dashboard/register")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/home")


class TestRegistrationWithoutNames:
    @pytest.fixture(autouse=True)
    def _open_registration_without_names(self, db_reset):
        factories.make_setting(db_reset, "allow_registration", "1")
        factories.make_setting(db_reset, "allow_first_name_last_name", "0")

    def test_name_fields_are_not_rendered(self, anon_client):
        body = anon_client.get("/dashboard/register").data
        assert b'name="firstname"' not in body
        assert b'name="lastname"' not in body

    def test_registration_works_without_names(self, app, anon_client):
        payload = register_payload()
        payload.pop("firstname")
        payload.pop("lastname")

        response = anon_client.post("/dashboard/register", data=payload)

        assert response.status_code == 302
        with app.app_context():
            user = User.query.filter_by(username="ada").one()
            assert user.firstname is None
            assert user.lastname is None


class TestForgotPassword:
    def test_page_renders(self, anon_client):
        assert anon_client.get("/dashboard/forgot-password").status_code == 200

    def test_known_email_sends_message(self, app, member, anon_client, monkeypatch):
        sent = []
        monkeypatch.setattr("core.extensions.mail.send", lambda message: sent.append(message))

        response = anon_client.post("/dashboard/forgot-password", data={"email": member.email})

        assert response.status_code == 200
        assert len(sent) == 1
        assert sent[0].recipients == [member.email]
        assert "reset-password" in sent[0].body

    def test_unknown_email_sends_nothing_but_says_it_did(self, app, anon_client, monkeypatch):
        """User enumeration is prevented by returning the same message."""
        sent = []
        monkeypatch.setattr("core.extensions.mail.send", lambda message: sent.append(message))

        response = anon_client.post("/dashboard/forgot-password", data={"email": "ghost@example.com"})

        assert sent == []
        assert b"reset instructions have been sent" in response.data

    def test_mail_failure_flashes_error(self, app, member, anon_client, monkeypatch):
        def boom(message):
            raise RuntimeError("SMTP down")

        monkeypatch.setattr("core.extensions.mail.send", boom)

        response = anon_client.post(
            "/dashboard/forgot-password", data={"email": member.email}, follow_redirects=True
        )

        assert b"Failed to send email" in response.data

    def test_invalid_email_format_is_rejected(self, anon_client):
        """The form rejects it, but ``forgot-password.html`` renders no errors.

        Consequence: submitting a malformed address looks like a no-op to the
        user -- the page simply re-renders with an empty field and no message.
        """
        response = anon_client.post("/dashboard/forgot-password", data={"email": "nope"})
        assert response.status_code == 200
        assert b"Enter a valid email" not in response.data
        assert b"fd-auth-error" not in response.data


class TestResetPassword:
    def _token(self, app, member):
        with app.app_context():
            return generate_reset_token(db.session.get(User, member.id))

    def test_valid_token_renders_form(self, app, member, anon_client):
        response = anon_client.get(f"/dashboard/reset-password/{self._token(app, member)}")
        assert response.status_code == 200
        assert b"New Password" in response.data

    def test_invalid_token_redirects(self, anon_client):
        response = anon_client.get("/dashboard/reset-password/garbage")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/forgot-password")

    def test_valid_reset_changes_password(self, app, member, anon_client):
        token = self._token(app, member)
        response = anon_client.post(
            f"/dashboard/reset-password/{token}",
            data={"password": ALT_PASSWORD, "retype_password": ALT_PASSWORD},
        )

        assert response.status_code == 302
        with app.app_context():
            user = db.session.get(User, member.id)
            assert user.check_password(ALT_PASSWORD)

    def test_mismatched_reset_is_rejected(self, app, member, anon_client):
        token = self._token(app, member)
        response = anon_client.post(
            f"/dashboard/reset-password/{token}",
            data={"password": ALT_PASSWORD, "retype_password": "Different1!x"},
        )

        assert response.status_code == 200
        assert b"Passwords do not match" in response.data
        with app.app_context():
            assert db.session.get(User, member.id).check_password(DEFAULT_PASSWORD)

    def test_weak_password_is_rejected(self, app, member, anon_client):
        token = self._token(app, member)
        anon_client.post(
            f"/dashboard/reset-password/{token}",
            data={"password": "aaaaaa", "retype_password": "aaaaaa"},
        )

        with app.app_context():
            assert db.session.get(User, member.id).check_password(DEFAULT_PASSWORD)

    def test_token_is_single_use_after_success(self, app, member, anon_client):
        token = self._token(app, member)
        anon_client.post(
            f"/dashboard/reset-password/{token}",
            data={"password": ALT_PASSWORD, "retype_password": ALT_PASSWORD},
        )

        response = anon_client.get(f"/dashboard/reset-password/{token}")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/dashboard/forgot-password")

    def test_reset_does_not_log_the_user_in(self, app, member, anon_client):
        token = self._token(app, member)
        anon_client.post(
            f"/dashboard/reset-password/{token}",
            data={"password": ALT_PASSWORD, "retype_password": ALT_PASSWORD},
        )

        assert anon_client.get("/dashboard/home").status_code == 302


class TestFlashMessaging:
    def test_registration_disabled_flash_is_visible(self, anon_client):
        response = anon_client.get("/dashboard/register", follow_redirects=True)
        assert flash_messages(response)
