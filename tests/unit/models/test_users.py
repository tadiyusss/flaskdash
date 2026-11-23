"""Unit tests for the user, role and login-history models."""

from __future__ import annotations

import pytest

from core.extensions import db
from core.models.users import LoginHistory, Role, User, UserRole
from tests.support import factories
from tests.support.constants import ALT_PASSWORD, DEFAULT_PASSWORD


pytestmark = pytest.mark.usefixtures("db_reset")


class TestPasswordHashing:
    def test_password_is_never_stored_in_plaintext(self, app, admin):
        with app.app_context():
            stored = db.session.get(User, admin.id).password

        assert stored != admin.password
        assert stored.startswith(("scrypt:", "pbkdf2:"))

    def test_check_password_accepts_correct_password(self, app, admin):
        with app.app_context():
            assert db.session.get(User, admin.id).check_password(DEFAULT_PASSWORD)

    def test_check_password_rejects_wrong_password(self, app, admin):
        with app.app_context():
            assert not db.session.get(User, admin.id).check_password("WrongPass1!")

    @pytest.mark.parametrize("bad", ["", " ", DEFAULT_PASSWORD + " "])
    def test_check_password_rejects_near_misses(self, app, admin, bad):
        with app.app_context():
            assert not db.session.get(User, admin.id).check_password(bad)

    def test_check_password_with_none_raises(self, app, admin):
        """Documented defect: ``check_password(None)`` raises AttributeError.

        The login view always passes ``form.password.data`` (a string), so this
        is a robustness issue rather than an exploitable one, but the raise is
        recorded here so a future fix is visible as a deliberate change.
        """
        with app.app_context():
            with pytest.raises(AttributeError):
                db.session.get(User, admin.id).check_password(None)

    def test_set_password_updates_stored_hash(self, app, member):
        with app.app_context():
            user = db.session.get(User, member.id)
            old_hash = user.password
            user.set_password(ALT_PASSWORD)
            db.session.refresh(user)

            assert user.password != old_hash
            assert user.check_password(ALT_PASSWORD)
            assert not user.check_password(DEFAULT_PASSWORD)

    def test_each_hash_is_salted(self, app):
        first = factories.make_user(app, username="salt1")
        second = factories.make_user(app, username="salt2")

        with app.app_context():
            assert db.session.get(User, first.id).password != db.session.get(User, second.id).password


class TestRoleAssignment:
    def test_set_roles_assigns_single_role(self, app, member):
        with app.app_context():
            user = db.session.get(User, member.id)
            assert [link.role.name for link in user.user_roles] == ["User"]

    def test_set_roles_replaces_previous_roles(self, app, member):
        with app.app_context():
            user = db.session.get(User, member.id)
            user.set_roles(["Editor"])
            db.session.expire_all()
            names = [link.role.name for link in db.session.get(User, member.id).user_roles]
            link_count = UserRole.query.count()

        assert names == ["Editor"]
        assert link_count == 1

    def test_set_roles_accepts_multiple_roles(self, app, member):
        with app.app_context():
            db.session.get(User, member.id).set_roles(["Editor", "Administrator"])
            names = sorted(link.role.name for link in db.session.get(User, member.id).user_roles)

        assert names == ["Administrator", "Editor"]

    def test_set_roles_ignores_unknown_role_names(self, app, member):
        with app.app_context():
            db.session.get(User, member.id).set_roles(["Nonexistent"])
            assert db.session.get(User, member.id).user_roles == []

    def test_set_roles_with_empty_list_removes_all(self, app, member):
        with app.app_context():
            db.session.get(User, member.id).set_roles([])
            assert db.session.get(User, member.id).user_roles == []

    def test_has_role_reflects_assignment(self, app, admin):
        with app.app_context():
            user = db.session.get(User, admin.id)
            assert user.has_role("Administrator") is True
            assert user.has_role("Editor") is False

    def test_has_role_is_false_without_roles(self, app):
        record = factories.make_user(app, username="roleless", roles=())
        with app.app_context():
            assert db.session.get(User, record.id).has_role("Administrator") is False

    def test_duplicate_user_role_pair_is_rejected(self, app, member):
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            user = db.session.get(User, member.id)
            db.session.add(UserRole(user_id=user.id, role_id=user.user_roles[0].role_id))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestModelConstraints:
    def test_duplicate_username_rejected(self, app, member):
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            db.session.add(User(username=member.username, email="other@example.com", password="x"))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_duplicate_email_rejected(self, app, member):
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            db.session.add(User(username="unique-name", email=member.email, password="x"))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_uid_is_generated_and_unique(self, app):
        first = factories.make_user(app, username="uid1")
        second = factories.make_user(app, username="uid2")

        assert first.uid and second.uid
        assert first.uid != second.uid
        assert len(first.uid) == 36

    def test_duplicate_role_name_rejected(self, app):
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            db.session.add(Role(name="User", description="duplicate"))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_default_profile_image(self, app, member):
        with app.app_context():
            assert db.session.get(User, member.id).profile_image == "default-avatar.jpg"

    def test_repr_contains_username_and_uid(self, app, member):
        with app.app_context():
            text = repr(db.session.get(User, member.id))

        assert member.username in text
        assert member.uid in text


class TestCascades:
    def test_deleting_user_removes_user_roles(self, app, member):
        with app.app_context():
            assert UserRole.query.count() == 1
            db.session.delete(db.session.get(User, member.id))
            db.session.commit()
            assert UserRole.query.count() == 0

    def test_deleting_user_removes_login_history(self, app, member):
        factories.make_login_history(app, member.id)
        with app.app_context():
            assert LoginHistory.query.count() == 1
            db.session.delete(db.session.get(User, member.id))
            db.session.commit()
            assert LoginHistory.query.count() == 0

    def test_deleting_role_removes_user_role_links(self, app, member):
        factories.make_role(app, "Temporary")
        with app.app_context():
            db.session.get(User, member.id).set_roles(["Temporary"])
            assert UserRole.query.count() == 1

            db.session.delete(Role.query.filter_by(name="Temporary").first())
            db.session.commit()

            assert UserRole.query.count() == 0
            # the user itself survives with no roles
            assert db.session.get(User, member.id) is not None
            assert db.session.get(User, member.id).user_roles == []

    def test_delete_login_history_helper(self, app, member):
        factories.make_login_history(app, member.id)
        with app.app_context():
            user = db.session.get(User, member.id)
            user.delete_login_history()
            assert LoginHistory.query.filter_by(user_id=member.id).count() == 0


class TestDeleteProfileImage:
    def test_default_avatar_is_not_deleted(self, app, member, monkeypatch):
        removed = []
        monkeypatch.setattr("os.remove", lambda path: removed.append(path))

        with app.app_context():
            db.session.get(User, member.id).delete_profile_image()

        assert removed == []

    def test_missing_custom_image_is_tolerated(self, app, member):
        with app.app_context():
            user = db.session.get(User, member.id)
            user.profile_image = "definitely-not-here.png"
            db.session.commit()
            user.delete_profile_image()  # must not raise

    def test_custom_image_is_removed(self, app, member, monkeypatch):
        removed = []
        monkeypatch.setattr("os.remove", lambda path: removed.append(path))

        with app.app_context():
            user = db.session.get(User, member.id)
            user.profile_image = "custom.png"
            db.session.commit()
            user.delete_profile_image()

        assert len(removed) == 1
        assert removed[0].endswith("custom.png")


class TestLoginHistory:
    def test_second_login_in_same_second_violates_unique_constraint(self, app, member, monkeypatch):
        """Regression: UNIQUE(user_id, timestamp) breaks rapid re-login.

        ``LoginHistory.timestamp`` defaults to ``CURRENT_TIMESTAMP`` (second
        resolution).  Two logins by one user within the same second therefore
        collide and ``/dashboard/`` returns HTTP 500.  The view's insert is
        pinned to a fixed timestamp here so the collision is deterministic
        instead of depending on wall-clock timing.
        """
        from datetime import datetime

        import core.views.auth as auth_views

        fixed = datetime(2026, 1, 1, 12, 0, 0)

        with app.app_context():
            db.session.add(LoginHistory(user_id=member.id, ip_address="127.0.0.1", timestamp=fixed))
            db.session.commit()

        class FixedTimestampHistory(LoginHistory):
            """Same table/constraints, but a deterministic timestamp default."""

            def __init__(self, **kwargs):
                kwargs.setdefault("timestamp", fixed)
                super().__init__(**kwargs)

        monkeypatch.setattr(auth_views, "LoginHistory", FixedTimestampHistory)

        response = app.test_client().post(
            "/dashboard/", data={"email": member.email, "password": DEFAULT_PASSWORD}
        )

        assert response.status_code == 500
        with app.app_context():
            assert LoginHistory.query.count() == 1
