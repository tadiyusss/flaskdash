"""Pytest fixtures for FlaskDash.

Design notes
------------
* The application is built **once per session**.  ``create_app`` mutates
  module-level registries (``core.utils.registry.*``) on every call, so calling
  it per test would silently accumulate duplicate settings categories and
  analytics grids.  A single instance plus a per-test database reset keeps each
  test isolated without touching those globals.
* ``db_reset`` drops and recreates every table and re-seeds the defaults the
  application expects (roles, settings), so a test can never leak rows.
* ``storage`` redirects every filesystem writer into a temporary directory.
  Without it, upload tests would litter ``core/static/uploads`` and ``media/``
  in the working tree.
* ``PROPAGATE_EXCEPTIONS`` is disabled for the test app so that a view raising
  an exception yields a 500 response we can assert on instead of aborting the
  test run.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

import core.views.system as system_views
import core.views.users as users_views
from core import create_app
from core.defaults import DEFAULT_ROLES, DEFAULT_SETTINGS_CATEGORY
from core.extensions import db
from core.models.settings import Setting, SettingCategory
from core.models.users import Role
from core.route import core
from config import TestingConfig
from tests.support import factories
from tests.support.constants import DEFAULT_PASSWORD
from tests.support.http import login as _login
from tests.support.http import login_via_form as _login_via_form


def _seed_defaults() -> None:
    """Insert the rows ``create_app`` would normally create on first boot."""
    for role in DEFAULT_ROLES:
        db.session.add(Role(name=role.name, description=role.description))

    for category in DEFAULT_SETTINGS_CATEGORY:
        db.session.add(
            SettingCategory(
                name=category.name,
                nice_name=category.nice_name,
                description=category.description,
            )
        )
        db.session.flush()
        for item in category.settings:
            if isinstance(item.value, bool):
                value = "1" if item.value else "0"
            elif item.value is None:
                value = ""
            else:
                value = str(item.value)
            db.session.add(
                Setting(
                    name=item.name,
                    key=item.key,
                    value=value,
                    category_name=category.name,
                )
            )
    db.session.commit()


@pytest.fixture(scope="session")
def app():
    application, _socketio = create_app(TestingConfig)
    application.config.update(
        PROPAGATE_EXCEPTIONS=False,
        WTF_CSRF_ENABLED=False,
        SERVER_NAME=None,
    )
    yield application


@pytest.fixture()
def db_reset(app):
    """Empty database with default roles/settings, for one test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        _seed_defaults()
    return app


@pytest.fixture()
def storage(app, db_reset, monkeypatch):
    """Point every upload/media writer at a throwaway directory tree.

    Yields the media root (``<tmp>/app/media``).  ``core/static`` is remapped to
    ``<tmp>/app/core/static`` and the working directory is switched to
    ``<tmp>/app`` so the views that use relative paths (``media/``,
    ``core/static/uploads``) stay inside the sandbox as well.
    """
    root = Path(tempfile.mkdtemp(prefix="flaskdash-test-"))
    app_dir = root / "app"
    static_dir = app_dir / "core" / "static"
    media_dir = app_dir / "media"
    views_dir = app_dir / "core" / "views"

    for directory in (
        static_dir / "uploads",
        static_dir / "images" / "profiles",
        media_dir / "profiles",
        views_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    # system.py derives the media root from ``Path(__file__)`` at call time.
    (views_dir / "system.py").write_text("")

    # ``media.py`` passes the literal "../media" to ``send_from_directory``,
    # which resolves against ``app.root_path`` -- so it always points at the
    # real repository. Rebinding the helper keeps werkzeug's path-traversal
    # protection intact while redirecting the lookup into the sandbox.
    import core.views.media as media_views

    real_send_from_directory = media_views.send_from_directory

    def sandboxed_send_from_directory(_directory, filename, **kwargs):
        return real_send_from_directory(str(media_dir), filename, **kwargs)

    monkeypatch.chdir(app_dir)
    monkeypatch.setattr(core, "static_folder", str(static_dir))
    monkeypatch.setattr(users_views, "MEDIA_FOLDER", media_dir)
    monkeypatch.setattr(system_views, "__file__", str(views_dir / "system.py"))
    monkeypatch.setattr(media_views, "send_from_directory", sandboxed_send_from_directory)

    try:
        yield media_dir
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture()
def client(app, db_reset):
    return app.test_client()


@pytest.fixture()
def admin(app, db_reset):
    return factories.make_admin(app)


@pytest.fixture()
def member(app, db_reset):
    return factories.make_member(app)


@pytest.fixture()
def admin_client(app, admin):
    return _login(app, admin)


@pytest.fixture()
def member_client(app, member):
    return _login(app, member)


@pytest.fixture()
def anon_client(app, db_reset):
    return app.test_client()


@pytest.fixture()
def login(app):
    """``login(app, user_record)`` -> authenticated client."""
    return _login


@pytest.fixture()
def login_form(app):
    """``login_form(app, email, password)`` -> client authenticated via POST."""
    return _login_via_form


# ---------------------------------------------------------------------------
# Backwards-compatible aliases for the pre-existing test modules.
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_session(db_reset):
    with db_reset.app_context():
        yield db.session


@pytest.fixture()
def fake_user(app, db_reset):
    return factories.make_user(app, username="fakeuser", password=DEFAULT_PASSWORD)


@pytest.fixture()
def admin_user(app, db_reset):
    return factories.make_admin(app)


@pytest.fixture()
def normal_user(app, db_reset):
    return factories.make_member(app, username="normaluser")


@pytest.fixture(autouse=True)
def _quiet_logging(monkeypatch):
    """Silence the application's DEBUG logging during tests."""
    import logging

    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def _restore_cwd():
    """Guard against a test leaving the process in a temporary directory.

    ``os.getcwd()`` raises once the directory has been removed, so the check
    falls back to restoring the original working directory blindly.
    """
    original = os.getcwd()

    def current() -> str | None:
        try:
            return os.getcwd()
        except (FileNotFoundError, OSError):
            return None

    yield
    if current() != original:
        os.chdir(original)
