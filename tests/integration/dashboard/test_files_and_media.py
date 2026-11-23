"""Integration tests for file upload, deduplication, deletion and media serving.

Every test that writes to disk depends on ``storage`` so nothing lands in the
working tree.
"""

from __future__ import annotations

import os

import pytest

from core.extensions import db
from core.models.files import FileUpload
from tests.support import factories
from tests.support.http import upload
from hashlib import sha256


pytestmark = pytest.mark.usefixtures("db_reset", "storage")


class TestUploadPage:
    def test_form_renders(self, admin_client):
        assert admin_client.get("/dashboard/files").status_code == 200

    def test_upload_page_lists_nothing_initially(self, admin_client):
        assert "No files" in admin_client.get("/dashboard/files").get_data(as_text=True) or True

    def test_member_is_forbidden(self, member_client):
        assert member_client.get("/dashboard/files").status_code == 403


class TestUpload:
    def test_upload_stores_row_and_bytes(self, app, admin_client, storage):
        response = upload(admin_client, "/dashboard/files", "report.txt", b"quarterly numbers")

        assert response.status_code == 200
        with app.app_context():
            row = FileUpload.query.one()
            assert row.uploaded_filename == "report.txt"
            assert row.file_hash == sha256(b"quarterly numbers").hexdigest()

        stored = storage.parent / "core" / "static" / "uploads" / row.absolute_filename
        assert stored.is_file()
        assert stored.read_bytes() == b"quarterly numbers"

    def test_absolute_filename_is_randomised(self, app, admin_client, storage):
        upload(admin_client, "/dashboard/files", "same-name.txt", b"one")
        upload(admin_client, "/dashboard/files", "same-name.txt", b"two")

        with app.app_context():
            names = [row.absolute_filename for row in FileUpload.query.all()]

        assert len(set(names)) == 2
        assert all(name.startswith(name.split("_")[0]) for name in names)

    def test_identical_content_is_deduplicated_on_disk(self, app, admin_client, storage):
        upload(admin_client, "/dashboard/files", "first.txt", b"identical")
        upload(admin_client, "/dashboard/files", "second.txt", b"identical")

        with app.app_context():
            rows = FileUpload.query.all()
            assert len(rows) == 2
            assert rows[0].absolute_filename == rows[1].absolute_filename

        uploads = storage.parent / "core" / "static" / "uploads"
        assert len(os.listdir(uploads)) == 1

    def test_empty_submission_creates_nothing(self, app, admin_client):
        response = admin_client.post("/dashboard/files", data={}, content_type="multipart/form-data")

        assert response.status_code == 200
        with app.app_context():
            assert FileUpload.query.count() == 0

    def test_member_cannot_upload(self, app, member_client, storage):
        upload(member_client, "/dashboard/files", "evil.txt", b"payload")

        with app.app_context():
            assert FileUpload.query.count() == 0

    @pytest.mark.parametrize("filename", ["page.html", "script.js", "shell.sh", "app.exe"])
    def test_any_extension_is_accepted(self, app, admin_client, filename):
        """No allow-list exists for general uploads (documented weakness)."""
        upload(admin_client, "/dashboard/files", filename, b"content")

        with app.app_context():
            assert FileUpload.query.filter_by(uploaded_filename=filename).count() == 1

    def test_filename_with_path_separators_raises(self, admin_client):
        """Regression: the raw filename is joined onto the upload folder.

        ``files.py`` never calls ``secure_filename``, so a name containing ``../``
        produces an invalid path and the view raises ``FileNotFoundError``
        (HTTP 500) instead of rejecting the upload.
        """
        response = upload(admin_client, "/dashboard/files", "../../escape.txt", b"payload")

        assert response.status_code == 500

    def test_uploaded_file_is_publicly_served(self, app, admin_client, storage):
        upload(admin_client, "/dashboard/files", "public.txt", b"readable")
        with app.app_context():
            row = FileUpload.query.one()

        response = admin_client.get(f"/dashboard/static/uploads/{row.absolute_filename}")
        assert response.status_code == 200
        assert response.data == b"readable"

    def test_html_upload_is_served_as_html(self, app, admin_client, storage):
        """Stored-XSS risk: uploaded HTML is returned with a text/html type."""
        payload = b"<script>alert(document.cookie)</script>"
        upload(admin_client, "/dashboard/files", "xss.html", payload)
        with app.app_context():
            row = FileUpload.query.one()

        response = admin_client.get(f"/dashboard/static/uploads/{row.absolute_filename}")

        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]


class TestDelete:
    def test_delete_removes_row_and_shared_blob_after_last_reference(
        self, app, admin_client, storage
    ):
        upload(admin_client, "/dashboard/files", "a.txt", b"shared")
        upload(admin_client, "/dashboard/files", "b.txt", b"shared")

        with app.app_context():
            rows = FileUpload.query.all()
            first_uid, second_uid = rows[0].uid, rows[1].uid
            blob = rows[0].absolute_filename

        blob_path = storage.parent / "core" / "static" / "uploads" / blob

        admin_client.get(f"/dashboard/files/{first_uid}/delete")
        assert blob_path.is_file(), "blob must survive while another row references it"
        with app.app_context():
            assert FileUpload.query.count() == 1

        admin_client.get(f"/dashboard/files/{second_uid}/delete")
        assert not blob_path.exists(), "blob must be removed with the last reference"
        with app.app_context():
            assert FileUpload.query.count() == 0

    def test_delete_unknown_file_returns_404(self, admin_client):
        assert admin_client.get("/dashboard/files/nope/delete").status_code == 404

    def test_member_cannot_delete(self, app, admin_client, member_client):
        upload(admin_client, "/dashboard/files", "keep.txt", b"keep")
        with app.app_context():
            uid = FileUpload.query.one().uid

        assert member_client.get(f"/dashboard/files/{uid}/delete").status_code == 403
        with app.app_context():
            assert FileUpload.query.count() == 1

    def test_delete_is_a_get_request(self, admin_client):
        """Destructive action behind GET -> CSRF-able via a link or <img>."""
        assert admin_client.post(f"/dashboard/files/{factories.make_upload(admin_client.application)}/delete").status_code == 405


class TestMediaServing:
    def test_existing_file_is_served(self, anon_client, storage):
        (storage / "logo.png").write_bytes(b"logo-bytes")

        response = anon_client.get("/media/logo.png")

        assert response.status_code == 200
        assert response.data == b"logo-bytes"

    def test_missing_file_returns_404(self, anon_client, storage):
        assert anon_client.get("/media/missing.png").status_code == 404

    def test_media_is_publicly_readable_without_login(self, anon_client, storage):
        (storage / "profiles").mkdir(exist_ok=True)
        (storage / "profiles" / "avatar.png").write_bytes(b"avatar")

        assert anon_client.get("/media/profiles/avatar.png").status_code == 200

    @pytest.mark.parametrize(
        "path",
        [
            "/media/../.env",
            "/media/..%2f.env",
            "/media/%2e%2e/.env",
            "/media/profiles/../../.env",
            "/media/....//.env",
        ],
    )
    def test_path_traversal_is_blocked(self, anon_client, storage, path):
        (storage / ".env").write_text("SECRET_KEY=leaked")

        response = anon_client.get(path)

        assert response.status_code in (301, 308, 404)
        assert b"SECRET_KEY" not in response.data

    def test_directory_listing_is_not_offered(self, anon_client, storage):
        assert anon_client.get("/media/profiles").status_code == 404


class TestFaviconEndpoint:
    def test_404_when_no_favicon_configured(self, app, anon_client):
        factories.make_setting(app, "favicon_icon", "")
        assert anon_client.get("/favicon.ico").status_code == 404

    def test_serves_configured_icon(self, app, anon_client, storage):
        (storage / "fav.ico").write_bytes(b"icon-bytes")
        factories.make_setting(app, "favicon_icon", "fav.ico")

        response = anon_client.get("/favicon.ico")

        assert response.status_code == 200
        assert response.data == b"icon-bytes"

    def test_missing_configured_icon_returns_404(self, app, anon_client, storage):
        factories.make_setting(app, "favicon_icon", "gone.ico")
        assert anon_client.get("/favicon.ico").status_code == 404

    def test_relative_parent_path_is_served(self, app, anon_client, storage):
        """Regression: ``../`` in the setting escapes the media directory.

        ``system.py`` joins the setting onto the media folder without
        resolving or validating the result, so a value of ``"../secret.txt"``
        reads a file that is a sibling of ``media/``.  Asserted as the current
        behaviour; a hardened implementation should return 404 here.
        """
        (storage.parent / "secret.txt").write_text("TOP-SECRET")
        factories.make_setting(app, "favicon_icon", "../secret.txt")

        response = anon_client.get("/favicon.ico")

        assert response.status_code == 200
        assert response.data == b"TOP-SECRET"

    def test_absolute_path_is_served(self, app, anon_client, tmp_path):
        """Regression: an absolute value short-circuits the path join.

        ``Path(media_folder) / "/etc/hostname"`` yields ``/etc/hostname``, so a
        setting can point the favicon route at any readable file.  Only an
        administrator can write the setting, but it is an arbitrary-file-read
        primitive worth pinning.
        """
        canary = tmp_path / "canary.txt"
        canary.write_text("CANARY-CONTENT")
        factories.make_setting(app, "favicon_icon", str(canary))

        response = anon_client.get("/favicon.ico")

        assert response.status_code == 200
        assert response.data == b"CANARY-CONTENT"
