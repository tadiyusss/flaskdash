"""HTTP helpers and a session-injecting login shortcut.

Logging in through ``/dashboard/`` writes a ``LoginHistory`` row stamped with
``CURRENT_TIMESTAMP``, and ``login_history`` has a UNIQUE(user_id, timestamp)
constraint -- two logins inside the same second raise IntegrityError.  Tests
therefore authenticate by seeding the Flask session directly, which is both
faster and immune to that bug.  ``login_via_form`` exists so the bug itself can
be covered explicitly.
"""

from __future__ import annotations

from flask.testing import FlaskClient

from tests.support.constants import DEFAULT_PASSWORD


def login(app, record) -> FlaskClient:
    """Return a test client already authenticated as ``record``."""
    client = app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(record.id)
        session["_fresh"] = True
    return client


def login_via_form(app, email: str, password: str = DEFAULT_PASSWORD) -> FlaskClient:
    """Authenticate through the real login view (exercises LoginHistory)."""
    client = app.test_client()
    client.post("/dashboard/", data={"email": email, "password": password})
    return client


def logout(client: FlaskClient):
    return client.get("/dashboard/logout")


def get_text(client: FlaskClient, url: str, **kwargs) -> str:
    response = client.get(url, **kwargs)
    return response.get_data(as_text=True)


def post_form(client: FlaskClient, url: str, data: dict, **kwargs):
    return client.post(url, data=data, **kwargs)


def upload(client: FlaskClient, url: str, filename: str, content: bytes, field: str = "file"):
    """POST a single file as multipart/form-data."""
    return client.post(
        url,
        data={field: (__import__("io").BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


def flash_messages(response) -> list[str]:
    """Extract flash text from a rendered page (dashboard + auth layouts)."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")
    texts: list[str] = []
    for node in soup.select(".fd-toast, .fd-toast span, .fd-auth-flash-message"):
        text = node.get_text(strip=True)
        if text and text not in texts:
            texts.append(text)
    return texts
