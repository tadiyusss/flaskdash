"""CSRF, injection, escaping and security-header tests."""

from __future__ import annotations

import io
import re

import pytest

from core.extensions import db
from core.models.files import FileUpload
from core.models.settings import Setting
from core.models.users import User
from tests.support import factories
from tests.support.constants import DEFAULT_PASSWORD
from tests.support.http import flash_messages, upload


pytestmark = pytest.mark.usefixtures("db_reset")


class TestCsrfProtection:
    """``WTF_CSRF_ENABLED`` is on in production config; tests disable it globally."""

    @pytest.fixture()
    def csrf_app(self, app):
        """Re-enable CSRF enforcement for one test, then restore it."""
        previous = app.config["WTF_CSRF_ENABLED"]
        app.config["WTF_CSRF_ENABLED"] = True
        try:
            yield app
        finally:
            app.config["WTF_CSRF_ENABLED"] = previous

    def test_settings_post_without_token_is_rejected(self, csrf_app, admin_client):
        """Flask-WTF rejects the POST, and the settings template hides why.

        ``settings.html`` renders ``csrf_token`` as a hidden field and shows
        errors only for the setting rows, so a rejected submission looks
        identical to a no-op: HTTP 200, no message, nothing saved.
        """
        response = admin_client.post(
            "/dashboard/settings",
            data={"site_title": "Hijacked", "site_settings_submit": "Save Changes"},
        )

        assert response.status_code == 200
        assert factories.read_setting(csrf_app, "site_title") == "FlaskDash"
        assert b"CSRF" not in response.data, "expected the CSRF error to be swallowed"

    def test_settings_post_with_valid_token_is_accepted(self, csrf_app, admin_client):
        page = admin_client.get("/dashboard/settings").get_data(as_text=True)
        token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)

        admin_client.post(
            "/dashboard/settings",
            data={
                "site_title": "Legit",
                "site_description": "d",
                "site_theme": "default",
                "default_user_role": "User",
                "csrf_token": token,
                "site_settings_submit": "Save Changes",
            },
        )

        assert factories.read_setting(csrf_app, "site_title") == "Legit"

    def test_every_post_form_renders_a_csrf_token(self, admin_client, app):
        """Template-level check: each POST form must include ``hidden_tag``."""
        from tests.support.analysers import find_forms
        from tests.support.paths import TEMPLATES_DIR

        missing = []
        for path in sorted(TEMPLATES_DIR.rglob("*.html")):
            source = path.read_text(encoding="utf-8")
            for form in find_forms(source):
                if form["method"] == "post" and not form["has_csrf"]:
                    missing.append(f"{path.relative_to(TEMPLATES_DIR)}:{form['line']}")

        assert not missing, f"POST forms without a CSRF field: {missing}"

    def test_delete_endpoints_are_get_and_therefore_unprotected(self, app, admin_client, storage):
        """Finding: state-changing GETs cannot be CSRF-protected by Flask-WTF.

        A cross-site ``<img src="...">`` or link is enough to delete a user or
        file for any logged-in administrator.
        """
        target = factories.make_user(app, username="csrf-victim")

        # Plain GET, no token, no custom header -- equivalent to a cross-site <img>.
        response = admin_client.get(
            f"/dashboard/users/manage/{target.uid}/delete",
            headers={"Referer": "https://evil.example.com/attack.html"},
        )

        assert response.status_code == 302
        with app.app_context():
            assert db.session.get(User, target.id) is None


class TestAuthenticationInjection:
    @pytest.mark.parametrize(
        "email",
        [
            "' OR 1=1--",
            "admin@example.com'--",
            "' OR '1'='1' --",
            "'; DROP TABLE user;--",
            "admin@example.com' OR '1'='1",
            '" OR ""="',
        ],
    )
    def test_sql_metacharacters_in_email_do_not_bypass_login(self, app, admin, email):
        client = app.test_client()
        response = client.post("/dashboard/", data={"email": email, "password": "whatever1A"})

        assert response.status_code in (200, 400)
        assert client.get("/dashboard/home").status_code == 302

    def test_drop_table_payload_leaves_tables_intact(self, app, admin):
        client = app.test_client()
        client.post(
            "/dashboard/",
            data={"email": "'; DROP TABLE user;--", "password": "whatever1A"},
        )

        with app.app_context():
            assert User.query.count() >= 1

    def test_sql_metacharacters_in_registration_are_stored_verbatim(self, app):
        """Registration uses the ORM, so the payload is data, not SQL."""
        factories.make_setting(app, "allow_registration", "1")
        factories.make_setting(app, "allow_first_name_last_name", "0")
        # <= 20 chars so the form's Length(max=20) does not reject it first.
        payload_name = "b';DROP TABLE user--"

        app.test_client().post(
            "/dashboard/register",
            data={
                "username": payload_name,
                "email": "inject@example.com",
                "password": DEFAULT_PASSWORD,
                "retype_password": DEFAULT_PASSWORD,
            },
        )

        with app.app_context():
            assert User.query.filter_by(username=payload_name).one()
            assert User.query.count() == 1


class TestOutputEscaping:
    def test_username_with_markup_is_escaped_in_user_list(self, app, admin_client):
        factories.make_user(app, username="<img src=x onerror=alert(1)>")

        body = admin_client.get("/dashboard/users").get_data(as_text=True)

        assert "<img src=x onerror=alert(1)>" not in body
        assert "&lt;img" in body

    def test_email_with_script_tag_is_escaped(self, app, admin_client):
        factories.make_user(app, username="scripted", email="<script>alert(1)</script>@example.com")

        body = admin_client.get("/dashboard/users").get_data(as_text=True)

        assert "<script>alert(1)</script>" not in body

    def test_uploaded_filename_is_escaped(self, app, admin_client, storage):
        upload(admin_client, "/dashboard/files", "<svg onload=alert(1)>.txt", b"data")

        body = admin_client.get("/dashboard/files").get_data(as_text=True)

        assert "<svg onload=alert(1)>" not in body

    def test_setting_value_is_escaped_on_the_login_page(self, app, anon_client):
        factories.make_setting(app, "site_title", "<script>alert('xss')</script>")

        body = anon_client.get("/dashboard/").get_data(as_text=True)

        assert "<script>alert('xss')</script>" not in body

    def test_role_description_is_escaped(self, app, admin_client):
        factories.make_setting(app, "developer_mode", "1")
        factories.make_role(app, "XssRole", description="<script>alert(1)</script>")

        body = admin_client.get("/dashboard/roles").get_data(as_text=True)

        assert "<script>alert(1)</script>" not in body

    def test_only_trusted_icons_use_the_safe_filter(self):
        """``|safe`` must only be applied to the server-side icon markup."""
        from tests.support.paths import TEMPLATES_DIR

        usages = []
        for path in sorted(TEMPLATES_DIR.rglob("*.html")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "|safe" in line:
                    usages.append((path.name, number, line.strip()))

        assert usages, "expected the dashboard icon markup to use |safe"
        for name, number, line in usages:
            assert "icon" in line, f"{name}:{number} applies |safe to something other than an icon: {line}"


class TestHeaderHardening:
    EXPECTED_HEADERS = (
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
    )

    @pytest.mark.parametrize("header", EXPECTED_HEADERS)
    def test_hardening_header_is_missing(self, anon_client, header):
        """Finding: no security headers are configured anywhere in the app.

        Asserted as-is; each of these should be added (``after_request`` hook or
        a proxy) and the test flipped to assert presence.
        """
        response = anon_client.get("/dashboard/")

        assert header not in response.headers

    def test_hsts_absent_without_tls_configuration(self, anon_client):
        assert "Strict-Transport-Security" not in anon_client.get("/dashboard/").headers

    def test_no_server_side_stack_trace_leaks_in_production_config(self, app):
        """A 404 must not expose a traceback; 500s return the generic page."""
        response = app.test_client().get("/dashboard/no-such-page")

        assert response.status_code == 404
        assert b"Traceback" not in response.data

    def test_debug_is_off_in_the_base_config(self):
        from config import Config

        assert getattr(Config, "DEBUG", False) is False


class TestSecretHandling:
    def test_default_secret_key_is_a_placeholder(self):
        """Finding: ``Config.SECRET_KEY`` falls back to a shipped constant.

        Running without ``SECRET_KEY`` in the environment makes session cookies
        forgeable.  Asserted so the placeholder is a visible, testable fact.
        """
        from config import Config

        source_default = Config.SECRET_KEY
        assert source_default in {"dev-secret-key", "changeme!", ""}, source_default

    def test_env_file_is_git_ignored(self):
        import subprocess
        from tests.support.paths import PROJECT_ROOT

        result = subprocess.run(
            ["git", "check-ignore", "--quiet", ".env"],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )
        assert result.returncode == 0, ".env must never be committed"

    def test_dotenv_is_not_tracked_by_git(self):
        import subprocess
        from tests.support.paths import PROJECT_ROOT

        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )
        assert result.returncode != 0, ".env appears to be tracked by git"

    def test_password_never_appears_in_rendered_pages(self, app, admin_client):
        factories.make_user(app, username="secretive")

        for url in ("/dashboard/users", "/dashboard/profile", "/dashboard/home"):
            assert DEFAULT_PASSWORD.encode() not in admin_client.get(url).data, url

    def test_password_hash_is_not_rendered(self, app, admin_client):
        with app.app_context():
            hashed = User.query.first().password

        assert hashed.encode() not in admin_client.get("/dashboard/users").data


class TestUploadSafety:
    @pytest.mark.parametrize(
        "field, filename, snippet",
        [
            ("file", "../../escape.txt", "/dashboard/files"),
        ],
    )
    def test_filename_traversal_is_not_sanitised(self, app, admin_client, storage, field, filename, snippet):
        """Finding: ``files.py`` never calls ``secure_filename``.

        A filename containing path separators is joined onto the upload folder
        verbatim, which raises instead of storing a sanitised name.
        """
        response = upload(admin_client, snippet, filename, b"payload")

        assert response.status_code == 500
        with app.app_context():
            assert FileUpload.query.count() == 0

    def test_profile_upload_sanitises_the_extension_only(self, app, member_client, member):
        """``profile.py`` derives only the extension from ``secure_filename``."""
        payload = (io.BytesIO(b"data"), "../../x.png")

        member_client.post(
            "/dashboard/profile/edit/picture",
            data={"profile_image": payload},
            content_type="multipart/form-data",
        )

        with app.app_context():
            name = db.session.get(User, member.id).profile_image

        assert name != "../../x.png"
        assert "/" not in name and ".." not in name
        assert name.endswith(".png")

    def test_member_cannot_overwrite_another_users_avatar(self, app, member_client, admin):
        with app.app_context():
            before = db.session.get(User, admin.id).profile_image

        member_client.post(
            "/dashboard/profile/edit/picture",
            data={"profile_image": (io.BytesIO(b"data"), "x.png")},
            content_type="multipart/form-data",
        )

        with app.app_context():
            assert db.session.get(User, admin.id).profile_image == before
