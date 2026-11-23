"""Database factories.

Every factory opens its own application context and returns a plain snapshot
(``UserRecord``) instead of a live ORM instance.  Returning detached ORM
objects is the classic source of flaky Flask tests: the object expires when the
context is popped and later attribute access raises ``DetachedInstanceError``.
Only primitives cross the boundary here.
"""

from __future__ import annotations

from typing import Iterable, NamedTuple

from core.extensions import db
from core.models.files import FileUpload
from core.models.settings import Setting
from core.models.users import LoginHistory, Role, User
from tests.support.constants import DEFAULT_PASSWORD


class UserRecord(NamedTuple):
    id: int
    uid: str
    username: str
    email: str
    password: str


def make_user(
    app,
    username: str = "user",
    roles: Iterable[str] = ("User",),
    password: str = DEFAULT_PASSWORD,
    email: str | None = None,
    firstname: str = "Test",
    lastname: str = "User",
) -> UserRecord:
    """Create a persisted user, optionally attaching roles, and return it."""
    with app.app_context():
        user = User(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email or f"{username}@example.com",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        role_names = list(roles)
        if role_names:
            user.set_roles(role_names)

        return UserRecord(
            id=user.id,
            uid=user.uid,
            username=user.username,
            email=user.email,
            password=password,
        )


def make_admin(app, username: str = "admin", **kwargs) -> UserRecord:
    return make_user(app, username=username, roles=("Administrator",), **kwargs)


def make_member(app, username: str = "member", **kwargs) -> UserRecord:
    return make_user(app, username=username, roles=("User",), **kwargs)


def make_role(app, name: str, description: str = "Test role") -> str:
    """Create a role and return its ``uid``."""
    with app.app_context():
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        return role.uid


def make_setting(app, key: str, value: str) -> None:
    """Overwrite an existing setting, creating it when missing."""
    with app.app_context():
        setting = Setting.query.filter_by(key=key).first()
        if setting is None:
            setting = Setting(
                key=key,
                name=key.replace("_", " ").title(),
                value=value,
                category_name="site_settings",
            )
            db.session.add(setting)
        else:
            setting.value = value
        db.session.commit()


def read_setting(app, key: str) -> str | None:
    with app.app_context():
        setting = Setting.query.filter_by(key=key).first()
        return None if setting is None else setting.value


def delete_setting(app, key: str) -> None:
    with app.app_context():
        setting = Setting.query.filter_by(key=key).first()
        if setting is not None:
            db.session.delete(setting)
            db.session.commit()


def make_login_history(app, user_id: int, ip: str = "127.0.0.1") -> None:
    with app.app_context():
        db.session.add(LoginHistory(user_id=user_id, ip_address=ip))
        db.session.commit()


def make_upload(
    app,
    uploaded_filename: str = "document.txt",
    absolute_filename: str = "stored.txt",
    file_hash: str = "0" * 64,
) -> str:
    """Create a ``FileUpload`` row (no bytes written) and return its uid."""
    with app.app_context():
        upload = FileUpload(
            uploaded_filename=uploaded_filename,
            absolute_filename=absolute_filename,
            file_hash=file_hash,
        )
        db.session.add(upload)
        db.session.commit()
        return upload.uid
