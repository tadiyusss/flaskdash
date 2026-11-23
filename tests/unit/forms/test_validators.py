"""Unit tests for the password/username/email validators.

The application enforces a password policy in two places: ``Length(min=6)`` on
the field and the custom ``validate_password_*`` validators that require eight
characters plus upper, lower and digit.  These tests pin both layers so a
future change to one is caught.

DB-backed validators need an application *and* request context because
``current_user`` is read from ``validate_my_*``; the ``ctx`` fixture supplies
both.
"""

from __future__ import annotations

import pytest
from wtforms import ValidationError

from core.forms.validators import (
    validate_email_unique,
    validate_my_email_unique,
    validate_my_username_unique,
    validate_password_digit,
    validate_password_length,
    validate_password_lowercase_letter,
    validate_password_uppercase_letter,
    validate_role_name_unique,
    validate_username_unique,
)
from tests.support import factories


pytestmark = pytest.mark.usefixtures("db_reset")


class _Field:
    def __init__(self, data):
        self.data = data


@pytest.fixture()
def ctx(app):
    """Request context so DB-querying validators can run."""
    with app.test_request_context():
        yield


def _run(validator, value, form=None):
    with pytest.raises(ValidationError) as excinfo:
        validator(form, _Field(value))
    return str(excinfo.value)


class TestPasswordPolicy:
    @pytest.mark.parametrize("password", ["Aa1aaaa", "Short1A", ""])
    def test_too_short_is_rejected(self, password):
        assert "at least 8 characters" in _run(validate_password_length, password)

    @pytest.mark.parametrize("password", ["Passw0rd", "Aa1bbbbbbbb", "x" * 40 + "A1"])
    def test_eight_or_more_is_accepted(self, password):
        validate_password_length(None, _Field(password))  # must not raise

    def test_seven_characters_is_rejected(self):
        assert "at least 8 characters" in _run(validate_password_length, "!!!!!!!")

    def test_missing_uppercase_is_rejected(self):
        assert "uppercase" in _run(validate_password_uppercase_letter, "passw0rd1")

    def test_missing_lowercase_is_rejected(self):
        assert "lowercase" in _run(validate_password_lowercase_letter, "PASSW0RD1")

    def test_missing_digit_is_rejected(self):
        assert "digit" in _run(validate_password_digit, "PasswordHere")

    def test_strong_password_passes_every_rule(self):
        password = "Str0ngPassw0rd"
        for validator in (
            validate_password_length,
            validate_password_uppercase_letter,
            validate_password_lowercase_letter,
            validate_password_digit,
        ):
            validator(None, _Field(password))

    def test_unicode_digit_satisfies_digit_rule(self):
        """``str.isdigit()`` is used, so non-ASCII digits pass."""
        validate_password_digit(None, _Field("Password\u0660"))

    def test_symbols_without_digits_fail(self):
        assert "digit" in _run(validate_password_digit, "!!!!!!!")


class TestUniquenessValidators:
    def test_username_taken(self, app, member, ctx):
        assert "already exists" in _run(validate_username_unique, member.username)

    def test_username_free(self, ctx):
        validate_username_unique(None, _Field("brand-new-name"))

    def test_email_taken(self, app, member, ctx):
        assert "already exists" in _run(validate_email_unique, member.email)

    def test_email_free(self, ctx):
        validate_email_unique(None, _Field("free@example.com"))

    def test_role_name_taken(self, ctx):
        assert "already exists" in _run(validate_role_name_unique, "Administrator")

    def test_role_name_free(self, ctx):
        validate_role_name_unique(None, _Field("Auditor"))


class TestSelfAwareValidators:
    """``validate_my_*`` must allow a user to keep their current values."""

    @pytest.fixture()
    def as_member(self, app, member):
        with app.test_request_context():
            from flask import session

            session["_user_id"] = str(member.id)
            session["_fresh"] = True
            yield member

    def test_own_username_is_allowed(self, as_member):
        validate_my_username_unique(None, _Field(as_member.username))

    def test_own_email_is_allowed(self, as_member):
        validate_my_email_unique(None, _Field(as_member.email))

    def test_other_username_is_rejected(self, app, as_member):
        other = factories.make_user(app, username="taken-name")
        assert "already exists" in _run(validate_my_username_unique, other.username)

    def test_other_email_is_rejected(self, app, as_member):
        other = factories.make_user(app, username="email-owner", email="owner@example.com")
        assert "already exists" in _run(validate_my_email_unique, other.email)

    def test_anonymous_user_causes_attribute_error(self, app):
        """Documented defect: the validators assume an authenticated user.

        They are only wired into authenticated views, so this is latent, but it
        means the forms cannot be reused on public pages without a guard.
        """
        with app.test_request_context():
            with pytest.raises(AttributeError):
                validate_my_username_unique(None, _Field("anything"))
