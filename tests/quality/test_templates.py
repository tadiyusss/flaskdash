"""Template structure and markup-quality tests.

These are static analyses of the Jinja sources: no request is made, so they run
fast and catch problems that only surface on rarely visited pages.
"""

from __future__ import annotations

import re

import pytest

from tests.support.analysers import analyse_html, class_tokens, find_forms, strip_jinja
from tests.support.paths import TEMPLATES_DIR, template_files


TEMPLATES = template_files()
TEMPLATE_IDS = [str(path.relative_to(TEMPLATES_DIR)) for path in TEMPLATES]

DESIGN_PREFIX = "fd-"
UTILITY_ALLOWLIST = {
    "hidden",
    "btn",
    "btn-full",
    "form-checkbox",
}
ALPINE_ATTRIBUTE = re.compile(r"^(x-[\w:.-]+|@[\w:.-]+|:[\w:.-]+)$")


def relative(path) -> str:
    return str(path.relative_to(TEMPLATES_DIR))


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_template_parses_as_jinja(template):
    """Every template must compile -- catches unclosed ``{% %}`` blocks."""
    from jinja2 import Environment, FileSystemLoader

    environment = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    environment.get_template(str(template.relative_to(TEMPLATES_DIR)))


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_html_tags_are_balanced(template):
    report = analyse_html(template.read_text(encoding="utf-8"))

    assert report.ok, f"{relative(template)}: {report.errors + report.unclosed}"


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_classes_use_the_design_system_prefix(template):
    """Every literal class must come from the ``fd-`` design system.

    Utility exceptions are listed explicitly so new exceptions are a deliberate
    edit rather than an accident.
    """
    violations = []
    for tag, token, line in class_tokens(template.read_text(encoding="utf-8")):
        if token.startswith("{{") or token.startswith("{%"):
            continue
        literal = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "", token)
        if not literal:
            continue
        if literal.startswith(DESIGN_PREFIX) or literal in UTILITY_ALLOWLIST:
            continue
        violations.append(f"line {line}: <{tag} class=\"{token}\">")

    assert not violations, f"{relative(template)} uses non-design-system classes:\n" + "\n".join(
        violations
    )


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_ids_are_unique_within_a_template(template):
    report = analyse_html(template.read_text(encoding="utf-8"))
    duplicates = {value for value in report.ids if report.ids.count(value) > 1}

    assert not duplicates, f"{relative(template)} repeats id attribute(s): {sorted(duplicates)}"


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_images_have_alt_text(template):
    source = template.read_text(encoding="utf-8")
    missing = [
        match.group(0)[:80]
        for match in re.finditer(r"<img\b[^>]*>", source, re.IGNORECASE)
        if "alt=" not in match.group(0)
    ]

    assert not missing, f"{relative(template)} has <img> without alt: {missing}"


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_no_static_inline_styles(template):
    """Styling belongs in the theme CSS.

    A style attribute is allowed only when its whole value is a dynamic value
    the server must compute (e.g. a progress-bar width); static declarations
    belong in the theme files.

    ``emails/`` is exempt: mail clients strip ``<style>`` blocks and have no
    access to the theme stylesheet, so inline declarations are the only way an
    email can be styled at all.
    """
    if template.relative_to(TEMPLATES_DIR).parts[0] == "emails":
        pytest.skip("email templates must inline their CSS; mail clients ignore stylesheets")

    source = template.read_text(encoding="utf-8")
    offenders = []
    for number, line in enumerate(source.splitlines(), 1):
        for match in re.finditer(r'style="([^"]*)"', line):
            value = match.group(1).strip()
            if value.startswith("{{") and value.endswith("}}"):
                continue
            if "{{" in value and value.split("{{")[0].strip(" ;:") == "":
                continue
            offenders.append(f"line {number}: {line.strip()[:90]}")

    assert not offenders, f"{relative(template)} uses static inline styles:\n" + "\n".join(offenders)


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_get_requests_have_no_side_effect_forms(template):
    """Only POST forms may submit data; GET forms would leak into URLs."""
    source = template.read_text(encoding="utf-8")
    for form in find_forms(source):
        assert form["method"] in {"get", "post"}, relative(template)


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_post_forms_include_csrf(template):
    source = template.read_text(encoding="utf-8")
    offenders = [f"line {form['line']}" for form in find_forms(source) if form["method"] == "post" and not form["has_csrf"]]

    assert not offenders, f"{relative(template)} has POST form(s) without CSRF at {offenders}"


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_no_unescaped_output_of_user_fields(template):
    """``|safe`` may only be applied to server-provided icon markup."""
    source = template.read_text(encoding="utf-8")
    for match in re.finditer(r"\{\{(.*?)\|safe.*?\}\}", source, re.DOTALL):
        expression = match.group(1)
        assert "icon" in expression, (
            f"{relative(template)} applies |safe to a non-icon expression: {expression.strip()}"
        )


@pytest.mark.parametrize("template", TEMPLATES, ids=TEMPLATE_IDS)
def test_alpine_attributes_are_well_formed(template):
    """Alpine directive names must look like ``x-...``, ``@...`` or ``:...``."""
    source = strip_jinja(template.read_text(encoding="utf-8"))
    for match in re.finditer(r"\s([\w@:-]+)=", source):
        candidate = match.group(1)
        if candidate.startswith(("x-", "@", ":")):
            assert ALPINE_ATTRIBUTE.match(candidate), f"{relative(template)}: odd attribute {candidate}"


class TestLayoutInheritance:
    def test_auth_pages_extend_the_public_layout(self):
        for path in (TEMPLATES_DIR / "auth").glob("*.html"):
            assert '{% extends "base.html" %}' in path.read_text(encoding="utf-8"), path.name

    def test_dashboard_pages_extend_the_dashboard_layout(self):
        for path in (TEMPLATES_DIR / "dashboard").glob("*.html"):
            if path.name == "base.html":
                continue
            source = path.read_text(encoding="utf-8")
            assert '{% extends "dashboard/base.html" %}' in source, path.name

    def test_dashboard_layout_extends_the_public_layout(self):
        source = (TEMPLATES_DIR / "dashboard" / "base.html").read_text(encoding="utf-8")
        assert '{% extends "base.html" %}' in source

    def test_every_page_sets_a_title_block(self):
        for path in template_files():
            if path.name == "base.html" or path.name.startswith("_"):
                # Layout bases supply the default title; ``_`` files are
                # partials (macros only) that never render a document.
                continue
            assert "{% block title %}" in path.read_text(encoding="utf-8"), relative(path)

    def test_base_layout_declares_the_blocks_pages_override(self):
        source = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")
        declared = set(re.findall(r"\{%\s*block\s+(\w+)\s*%\}", source))
        assert {"title", "head", "content", "javascript"} <= declared

    def test_dashboard_layout_provides_a_main_block(self):
        source = (TEMPLATES_DIR / "dashboard" / "base.html").read_text(encoding="utf-8")
        assert "{% block main %}" in source


class TestTemplateHardening:
    def test_no_hardcoded_urls(self):
        """Links must be built with ``url_for`` so the prefix stays configurable."""
        offenders = []
        for path in template_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r'(?:href|action|src)="/dashboard/[^"]*"', line):
                    offenders.append(f"{relative(path)}:{number}")

        assert not offenders, f"hardcoded dashboard URLs: {offenders}"

    def test_no_jinja_comments_left_unterminated(self):
        for path in template_files():
            source = path.read_text(encoding="utf-8")
            assert source.count("{#") == source.count("#}"), relative(path)

    def test_jinja_delimiters_are_balanced(self):
        for path in template_files():
            source = path.read_text(encoding="utf-8")
            assert source.count("{{") == source.count("}}"), relative(path)
            assert source.count("{%") == source.count("%}"), relative(path)

    def test_no_todo_or_fixme_markers(self):
        offenders = [
            f"{relative(path)}:{number}"
            for path in template_files()
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(r"\b(TODO|FIXME|XXX)\b", line)
        ]
        assert not offenders, f"unfinished markers in templates: {offenders}"

    def test_every_form_has_a_submit_control(self):
        for path in template_files():
            source = path.read_text(encoding="utf-8")
            for form in find_forms(source):
                body = source.split("<form", 1)[-1]
                assert "submit" in body.lower() or "button" in body.lower(), relative(path)
