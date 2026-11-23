"""Shared constants for the test suite."""

from __future__ import annotations

# Passwords used by factories.  They must satisfy ``core.forms.validators``
# (>= 8 chars, upper, lower and a digit) so tests never fail for the wrong
# reason.
DEFAULT_PASSWORD = "Passw0rd!23"
ALT_PASSWORD = "An0ther!Pass"

ADMINISTRATOR = "Administrator"
EDITOR = "Editor"
MEMBER = "User"

DEFAULT_SETTING_KEYS = (
    "site_title",
    "favicon_icon",
    "website_logo",
    "site_description",
    "site_theme",
    "allow_registration",
    "allow_first_name_last_name",
    "default_user_role",
    "developer_mode",
)

# Endpoints that are intentionally reachable without a session.
PUBLIC_DASHBOARD_ENDPOINTS = frozenset(
    {
        "core.login",
        "core.register",
        "core.forgot_password",
        "core.reset_password",
        "core.static",
    }
)

# Valid 1x1 PNG payload; used wherever an image file is required.
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
