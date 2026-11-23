"""Unit tests for settings and file-upload models."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from core.extensions import db
from core.models.files import FileUpload
from core.models.settings import Setting, SettingCategory
from tests.support import factories


pytestmark = pytest.mark.usefixtures("db_reset")


class TestSettingCategory:
    def test_default_category_exists(self, app):
        with app.app_context():
            category = SettingCategory.query.filter_by(name="site_settings").first()
            assert category is not None
            assert category.nice_name == "Site Settings"

    def test_duplicate_category_name_rejected(self, app):
        with app.app_context():
            db.session.add(SettingCategory(name="site_settings", nice_name="Dup"))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_repr(self, app):
        with app.app_context():
            category = SettingCategory.query.first()
            assert repr(category) == f"<SettingCategory {category.name}>"


class TestSetting:
    def test_all_default_keys_are_registered(self, app):
        from tests.support.constants import DEFAULT_SETTING_KEYS

        with app.app_context():
            keys = {setting.key for setting in Setting.query.all()}

        assert set(DEFAULT_SETTING_KEYS) <= keys

    def test_to_dict_shape(self, app):
        with app.app_context():
            payload = Setting.query.filter_by(key="site_title").first().to_dict()

        assert set(payload) == {"id", "name", "key", "value"}
        assert payload["key"] == "site_title"

    def test_duplicate_key_rejected(self, app):
        with app.app_context():
            db.session.add(
                Setting(
                    name="Duplicate",
                    key="site_title",
                    value="x",
                    category_name="site_settings",
                )
            )
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_value_may_be_null(self, app):
        """``value`` is nullable (an explicit migration exists for it)."""
        with app.app_context():
            db.session.add(
                Setting(name="Nullable", key="nullable_key", value=None, category_name="site_settings")
            )
            db.session.commit()
            assert Setting.query.filter_by(key="nullable_key").first().value is None

    def test_boolean_settings_are_stored_as_strings(self, app):
        with app.app_context():
            for key in ("allow_registration", "allow_first_name_last_name", "developer_mode"):
                setting = Setting.query.filter_by(key=key).first()
                assert setting.value in {"0", "1"}

    def test_repr(self, app):
        with app.app_context():
            setting = Setting.query.filter_by(key="site_title").first()
            assert "site_title" in repr(setting)


class TestFileUpload:
    def test_uid_is_generated(self, app):
        uid = factories.make_upload(app, uploaded_filename="a.txt")
        assert len(uid) == 36

    def test_upload_date_defaults_to_now(self, app):
        factories.make_upload(app, uploaded_filename="dated.txt")
        with app.app_context():
            assert FileUpload.query.filter_by(uploaded_filename="dated.txt").first().upload_date

    def test_duplicate_uid_rejected(self, app):
        uid = factories.make_upload(app, uploaded_filename="first.txt")
        with app.app_context():
            db.session.add(
                FileUpload(
                    uid=uid,
                    uploaded_filename="second.txt",
                    absolute_filename="x.txt",
                    file_hash="1" * 64,
                )
            )
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_same_hash_allowed_for_multiple_rows(self, app):
        """Deduplication relies on several rows sharing one hash."""
        for name in ("one.txt", "two.txt"):
            factories.make_upload(app, uploaded_filename=name, absolute_filename="shared.txt", file_hash="a" * 64)

        with app.app_context():
            assert FileUpload.query.filter_by(file_hash="a" * 64).count() == 2

    def test_repr(self, app):
        factories.make_upload(app, uploaded_filename="repr.txt")
        with app.app_context():
            assert "repr.txt" in repr(FileUpload.query.first())
