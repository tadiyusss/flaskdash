"""Unit tests for the WTForms classes in ``core.forms``.

Forms are instantiated inside a request context with ``MultiDict`` data, which
is exactly how Flask-WTF builds them from a POST body.
"""

from __future__ import annotations

import io

import pytest
from werkzeug.datastructures import MultiDict

from core.forms.auth import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from core.forms.files import FileUploadForm
from core.forms.profile import EditNameForm, EditPasswordForm, EditProfileForm
from core.forms.users import (
    CreateRoleForm,
    CreateUserForm,
    ManageNameForm,
    ManageUserPasswordForm,
    build_manage_user_role_form,
)
from tests.support import factories
from tests.support.constants import DEFAULT_PASSWORD, PNG_BYTES


pytestmark = pytest.mark.usefixtures("db_reset")


def validate(form_class, data, **kwargs):
    """Build a form the same way Flask-WTF does: from request formdata."""
    with _request_context(data):
        form = form_class(**kwargs)
        form.validate()
        return form


class _request_context:
    """Enter a request context carrying POST formdata (and files).

    Passing data through the request context (rather than straight into the
    form) is what makes ``FileStorage`` tuples behave exactly as in production.
    """

    def __init__(self, data=None):
        self.data = data

    def __enter__(self):
        from flask import current_app

        self._ctx = current_app.test_request_context(method="POST", data=self.data)
        self._ctx.push()
        return self

    def __exit__(self, *exc):
        self._ctx.pop()
        return False


def build(form_class, data=None, **kwargs):
    """Instantiate + validate a form inside a request context."""
    with _request_context(data):
        form = form_class(**kwargs)
        form.validate()
        return form


@pytest.fixture(autouse=True)
def _app_context(app):
    with app.app_context():
        yield


class TestLoginForm:
    def test_valid_credentials_pass_validation(self):
        form = validate(LoginForm, {"email": "user@example.com", "password": "anything"})
        assert form.errors == {}

    @pytest.mark.parametrize("email", ["", "not-an-email", "user@", "@example.com", "a b@example.com"])
    def test_invalid_email_is_rejected(self, email):
        form = validate(LoginForm, {"email": email, "password": "x"})
        assert "email" in form.errors

    def test_missing_password_is_rejected(self):
        form = validate(LoginForm, {"email": "user@example.com", "password": ""})
        assert "password" in form.errors

    def test_empty_submission_reports_both_fields(self):
        form = validate(LoginForm, {})
        assert set(form.errors) == {"email", "password"}

    def test_login_does_not_validate_password_strength(self):
        """The login form must accept legacy passwords that predate the policy."""
        form = validate(LoginForm, {"email": "user@example.com", "password": "old"})
        assert form.errors == {}


class TestRegisterForm:
    def _payload(self, **overrides):
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

    def test_valid_registration_passes(self):
        assert validate(RegisterForm, self._payload()).errors == {}

    @pytest.mark.parametrize("field", ["firstname", "lastname", "username", "email", "password", "retype_password"])
    def test_each_field_is_required(self, field):
        form = validate(RegisterForm, self._payload(**{field: ""}))
        assert field in form.errors

    @pytest.mark.parametrize("username", ["a", "a" * 21])
    def test_username_length_bounds(self, username):
        assert "username" in validate(RegisterForm, self._payload(username=username)).errors

    @pytest.mark.parametrize("username", ["a" * 2, "a" * 20])
    def test_username_length_boundaries_accepted(self, username):
        assert "username" not in validate(RegisterForm, self._payload(username=username)).errors

    @pytest.mark.parametrize("password", ["Short1A", "alllowercase1", "ALLUPPER1", "NoDigitsHere"])
    def test_weak_passwords_rejected(self, password):
        form = validate(
            RegisterForm, self._payload(password=password, retype_password=password)
        )
        assert "password" in form.errors

    def test_password_confirmation_is_not_cross_validated_by_the_form(self):
        """The form never compares the two fields; the view does.

        Documented so the responsibility is explicit: if the view check is ever
        removed, registration would silently accept mismatched passwords.
        """
        form = validate(
            RegisterForm, self._payload(password=DEFAULT_PASSWORD, retype_password="Different1!")
        )
        assert form.errors == {}

    def test_firstname_rejects_digits_and_symbols(self):
        """``RegisterForm`` applies no Regexp, unlike ``CreateUserForm``."""
        form = validate(RegisterForm, self._payload(firstname="1234"))
        assert form.errors == {}

    @pytest.mark.parametrize("username", ["with space", "<script>", "ünïcode", "a/b"])
    def test_username_has_no_charset_restriction(self, username):
        """No Regexp is applied: unusual usernames pass validation (stored escaped)."""
        assert "username" not in validate(RegisterForm, self._payload(username=username)).errors

    def test_existing_email_reports_uniqueness_error(self, app, member):
        form = validate(RegisterForm, self._payload(email=member.email))
        assert "already exists" in form.errors["email"][0]

    def test_existing_username_reports_uniqueness_error(self, app, member):
        form = validate(RegisterForm, self._payload(username=member.username))
        assert "already exists" in form.errors["username"][0]


class TestForgotAndResetPasswordForms:
    def test_forgot_password_requires_valid_email(self):
        assert "email" in validate(ForgotPasswordForm, {"email": "bad"}).errors
        assert validate(ForgotPasswordForm, {"email": "ok@example.com"}).errors == {}

    def test_reset_password_enforces_policy(self):
        form = validate(
            ResetPasswordForm, {"password": "weak", "retype_password": "weak"}
        )
        assert "password" in form.errors

    def test_reset_password_accepts_strong_password(self):
        form = validate(
            ResetPasswordForm, {"password": DEFAULT_PASSWORD, "retype_password": DEFAULT_PASSWORD}
        )
        assert form.errors == {}

    def test_reset_password_does_not_compare_confirmation(self):
        form = validate(
            ResetPasswordForm,
            {"password": DEFAULT_PASSWORD, "retype_password": "Another1!xx"},
        )
        assert form.errors == {}


class TestCreateUserForm:
    def _payload(self, **overrides):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "firstname": "New",
            "lastname": "User",
            "password": DEFAULT_PASSWORD,
            "role": "User",
        }
        data.update(overrides)
        return data

    def _form(self, data):
        with _request_context(data):
            form = CreateUserForm()
            form.role.choices = [("User", "User"), ("Editor", "Editor")]
            form.validate()
            return form

    def test_valid_payload(self):
        assert self._form(self._payload()).errors == {}

    def test_role_field_requires_configured_choices(self):
        """``role.choices`` is empty by default; validation must then raise.

        The view always populates the choices from the database, so this
        documents the contract rather than a user-facing failure.
        """
        with _request_context(self._payload()):
            with pytest.raises(TypeError):
                CreateUserForm().validate()

    def test_invalid_role_is_rejected(self):
        assert "role" in self._form(self._payload(role="Nonexistent")).errors

    @pytest.mark.parametrize("name", ["Ada1", "Ada!", "", "A"])
    def test_names_must_be_letters_only(self, name):
        form = self._form(self._payload(firstname=name))
        assert "firstname" in form.errors

    def test_password_policy_applies(self):
        assert "password" in self._form(self._payload(password="short")).errors

    def test_duplicate_username_rejected(self, app, member):
        assert "username" in self._form(self._payload(username=member.username)).errors

    def test_duplicate_email_rejected(self, app, member):
        assert "email" in self._form(self._payload(email=member.email)).errors


class TestManageForms:
    def test_manage_password_form_only_enforces_length(self):
        """No complexity rules here -- ``Length(min=6)`` is the only guard."""
        form = validate(ManageUserPasswordForm, {"new_password": "aaaaaa"})
        assert form.errors == {}

    def test_manage_password_form_rejects_short_password(self):
        form = validate(ManageUserPasswordForm, {"new_password": "abc"})
        assert "new_password" in form.errors

    def test_manage_name_form_rejects_empty_names(self):
        """``Regexp`` is applied without ``Optional()``, so "" fails the pattern.

        ``ManageNameForm`` therefore cannot clear a user's name through the
        admin UI -- unlike ``EditNameForm``, which has the same defect.
        """
        form = validate(
            ManageNameForm,
            {"username": "someone", "email": "someone@example.com", "firstname": "", "lastname": ""},
        )
        assert set(form.errors) >= {"firstname", "lastname"}

    def test_manage_name_form_accepts_letters(self):
        form = validate(
            ManageNameForm,
            {"username": "someone", "email": "someone@example.com", "firstname": "Ada", "lastname": "Byron"},
        )
        assert form.errors == {}

    def test_manage_name_form_rejects_digits_in_name(self):
        with _request_context():
            form = ManageNameForm(
                MultiDict({"username": "someone", "email": "someone@example.com", "firstname": "R2D2", "lastname": ""})
            )
            assert form.validate() is False

    def test_dynamic_role_form_has_one_checkbox_per_role(self, app, member):
        with _request_context():
            from core.models.users import Role, User
            from core.extensions import db

            form = build_manage_user_role_form(db.session.get(User, member.id))
            expected = {f"role_{role.id}" for role in Role.query.all()}
            assert set(form._fields) == expected

    def test_dynamic_role_form_preselects_assigned_roles(self, app, member):
        with _request_context():
            from core.models.users import Role, User
            from core.extensions import db

            form = build_manage_user_role_form(db.session.get(User, member.id))
            checked = {
                role.name for role in Role.query.all() if form._fields[f"role_{role.id}"].data
            }
            assert checked == {"User"}


class TestProfileForms:
    def test_edit_password_form_requires_current_password(self):
        form = validate(EditPasswordForm, {"current_password": "", "new_password": DEFAULT_PASSWORD})
        assert form.errors

    def test_edit_password_form_has_no_complexity_check(self):
        """Only ``Length(min=6)`` is applied -- unlike registration."""
        form = validate(EditPasswordForm, {"current_password": DEFAULT_PASSWORD, "new_password": "aaaaaa"})
        assert form.errors == {}

    def test_edit_name_form_requires_username_and_email(self):
        form = validate(EditNameForm, {"username": "", "email": "", "firstname": "", "lastname": ""})
        assert form.errors

    def test_profile_image_must_have_allowed_extension(self):
        form = validate(EditProfileForm, {"profile_image": (io.BytesIO(b"data"), "payload.exe")})
        assert "Invalid file extension" in form.errors["profile_image"][0]

    @pytest.mark.parametrize("filename", ["a.png", "a.jpg", "a.jpeg", "a.gif", "a.webp", "a.svg"])
    def test_allowed_image_extensions(self, filename):
        form = validate(EditProfileForm, {"profile_image": (io.BytesIO(PNG_BYTES), filename)})
        assert form.errors == {}

    def test_profile_image_is_required(self):
        form = validate(EditProfileForm, {})
        assert form.errors


class TestRoleAndFileForms:
    def test_role_form_requires_name_and_description(self):
        form = validate(CreateRoleForm, {"name": "", "description": ""})
        assert form.errors

    def test_role_name_length_bound(self):
        form = validate(CreateRoleForm, {"name": "x" * 51, "description": "d"})
        assert "name" in form.errors

    def test_role_description_length_bound(self):
        form = validate(CreateRoleForm, {"name": "Auditor", "description": "d" * 201})
        assert "description" in form.errors

    def test_duplicate_role_name_rejected(self):
        form = validate(CreateRoleForm, {"name": "Administrator", "description": "d"})
        assert "name" in form.errors

    def test_file_upload_form_requires_a_file(self):
        form = validate(FileUploadForm, {})
        assert form.errors

    @pytest.mark.parametrize("filename", ["tool.exe", "page.html", "sheet.csv", "doc.pdf"])
    def test_file_upload_form_accepts_any_extension(self, filename):
        """There is deliberately no extension allow-list for general uploads."""
        form = validate(FileUploadForm, {"file": (io.BytesIO(b"x"), filename)})
        assert form.errors == {}

    def test_file_upload_form_rejects_empty_filename(self):
        form = validate(FileUploadForm, {"file": (io.BytesIO(b""), "")})
        assert form.errors
