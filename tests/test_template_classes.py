import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

# Matches {{ ... }} and {% ... %}
JINJA_PATTERN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)
MASK_CHAR = "\x00"

PREFIX = "fd-"

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "core" / "templates"


def mask_jinja(text: str) -> str:
    """Replace Jinja blocks with a placeholder."""
    return JINJA_PATTERN.sub(MASK_CHAR, text)


def check_template(template_path: Path):
    html = template_path.read_text(encoding="utf-8", errors="replace")

    soup = BeautifulSoup(
        html,
        "html.parser",
        multi_valued_attributes=None,
    )

    violations = []

    for tag in soup.find_all(True):
        raw_class = tag.get("class")
        if not raw_class:
            continue

        masked = mask_jinja(raw_class)

        for token in masked.split():

            literal = token.replace(MASK_CHAR, "")

            # Entirely Jinja
            if not literal:
                continue

            if not literal.startswith(PREFIX):
                violations.append(
                    {
                        "tag": tag.name,
                        "class": token.replace(MASK_CHAR, "{{...}}"),
                        "line": getattr(tag, "sourceline", None),
                    }
                )

    return violations


TEMPLATES = sorted(TEMPLATE_DIR.rglob("*.html"))


@pytest.mark.parametrize(
    "template",
    TEMPLATES,
    ids=lambda p: str(p.relative_to(TEMPLATE_DIR)),
)
def test_template_fd_classes(template):
    violations = check_template(template)

    if violations:
        messages = [
            f"{template.relative_to(TEMPLATE_DIR)}"
        ]

        for v in violations:
            line = v["line"] or "unknown"
            messages.append(
                f"  Line {line}: <{v['tag']}> class=\"{v['class']}\""
            )

        pytest.fail("\n".join(messages))