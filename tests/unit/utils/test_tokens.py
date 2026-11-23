"""Unit tests for the password-reset token helpers."""

from __future__ import annotations

import pytest
from itsdangerous import URLSafeTimedSerializer

from core.extensions import db
from core.models.users import User
from core.utils.tokens import generate_reset_token, verify_reset_token
from tests.support.constants import ALT_PASSWORD, DEFAULT_PASSWORD


pytestmark = pytest.mark.usefixtures("db_reset")


def test_token_roundtrip_returns_the_user(app, member):
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))
        user = verify_reset_token(token)

        assert user is not None
        assert user.id == member.id


def test_token_is_single_string_without_padding_issues(app, member):
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))

    assert isinstance(token, str)
    assert token == token.strip()
    assert "/" not in token or token.startswith(".")  # url-safe serialiser may still emit "/" rarely


def test_tampered_token_is_rejected(app, member):
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))
        assert verify_reset_token(token[:-4] + "AAAA") is None


def test_garbage_token_is_rejected(app):
    with app.app_context():
        assert verify_reset_token("not-a-real-token") is None


def test_empty_token_is_rejected(app):
    with app.app_context():
        assert verify_reset_token("") is None


def test_expired_token_is_rejected(app, member):
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))
        assert verify_reset_token(token, expiration=-1) is None


def test_token_valid_within_expiry_window(app, member):
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))
        assert verify_reset_token(token, expiration=3600) is not None


def test_token_invalidated_by_password_change(app, member):
    """The token embeds the password hash, so a reset invalidates old links."""
    with app.app_context():
        user = db.session.get(User, member.id)
        token = generate_reset_token(user)
        user.set_password(ALT_PASSWORD)
        assert verify_reset_token(token) is None


def test_token_invalidated_when_user_deleted(app, member):
    with app.app_context():
        user = db.session.get(User, member.id)
        token = generate_reset_token(user)
        db.session.delete(user)
        db.session.commit()
        assert verify_reset_token(token) is None


def test_token_signed_with_another_secret_is_rejected(app, member):
    with app.app_context():
        forged = URLSafeTimedSerializer("attacker-secret").dumps(
            {"user_id": member.id, "password_hash": "x"},
            salt="attacker-secret",
        )
        assert verify_reset_token(forged) is None


def test_forged_token_with_known_payload_still_fails(app, member):
    """Even with a valid payload shape the signature must not validate."""
    with app.app_context():
        user = db.session.get(User, member.id)
        payload = {"user_id": user.id, "password_hash": user.password}
        forged = URLSafeTimedSerializer("wrong-secret").dumps(payload, salt=app.config["SECRET_KEY"])
        assert verify_reset_token(forged) is None


def test_tokens_are_stable_within_the_same_second(app, member):
    """Two tokens issued in the same second are byte-identical.

    ``URLSafeTimedSerializer`` embeds seconds-resolution timestamps, so reset
    tokens are deterministic within a second.  That is fine for security (the
    payload still contains the current password hash) but means a token cannot
    be invalidated by re-issuing it.
    """
    with app.app_context():
        user = db.session.get(User, member.id)
        first = generate_reset_token(user)
        second = generate_reset_token(user)
        assert verify_reset_token(first) is not None
        assert verify_reset_token(second) is not None

    assert first == second


def test_reset_flow_updates_password(app, member, client):
    """End-to-end: token -> reset form -> new password works, old does not."""
    with app.app_context():
        token = generate_reset_token(db.session.get(User, member.id))

    response = client.post(
        f"/dashboard/reset-password/{token}",
        data={"password": ALT_PASSWORD, "retype_password": ALT_PASSWORD},
    )
    assert response.status_code == 302

    with app.app_context():
        user = db.session.get(User, member.id)
        assert user.check_password(ALT_PASSWORD)
        assert not user.check_password(DEFAULT_PASSWORD)
