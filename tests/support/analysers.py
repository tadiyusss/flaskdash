"""Source-text analysers used by the code-format and template-quality tests.

These helpers parse templates and Python sources as *data*; they never import
or execute the code under inspection, so a style regression is reported as a
failing assertion rather than an import error.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)

JINJA_NODE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)


def strip_jinja(text: str) -> str:
    """Remove Jinja expressions/statements so an HTML parser is not confused."""
    return JINJA_NODE.sub("", text)


@dataclass
class HtmlReport:
    errors: list[str] = field(default_factory=list)
    unclosed: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.unclosed


class _BalancedHtmlParser(HTMLParser):
    """Track open/close pairs and collect ``id`` attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag in VOID_ELEMENTS:
            return
        self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        line = self.getpos()[0]
        if not self.stack:
            self.errors.append(f"line {line}: stray closing </{tag}>")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        open_tags = [name for name, _ in self.stack]
        if tag in open_tags:
            index = len(open_tags) - 1 - open_tags[::-1].index(tag)
            for name, opened_at in self.stack[index + 1 :]:
                self.errors.append(f"line {opened_at}: <{name}> closed by </{tag}> but opened later")
            del self.stack[index:]
            self.stack.pop() if self.stack and self.stack[-1][0] == tag else None
        else:
            self.errors.append(f"line {line}: </{tag}> does not match any open element")


def analyse_html(source: str) -> HtmlReport:
    parser = _BalancedHtmlParser()
    parser.feed(strip_jinja(source))
    parser.close()
    return HtmlReport(
        errors=parser.errors,
        unclosed=[f"line {line}: <{name}> never closed" for name, line in parser.stack],
        ids=parser.ids,
    )


def class_tokens(source: str) -> list[tuple[str, str, int]]:
    """Return ``(tag, class_token, line)`` for every literal class in a template."""

    class _ClassCollector(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.tokens: list[tuple[str, str, int]] = []

        def handle_starttag(self, tag, attrs) -> None:
            for name, value in attrs:
                if name == "class" and value:
                    for token in value.split():
                        self.tokens.append((tag, token, self.getpos()[0]))

        handle_startendtag = handle_starttag

    collector = _ClassCollector()
    collector.feed(source)
    return collector.tokens


def find_forms(source: str) -> list[dict]:
    """Small form scanner: HTTP method plus presence of a CSRF field.

    Scans the *original* template text so that ``{{ form.hidden_tag() }}``
    (removed by :func:`strip_jinja`) still counts as a CSRF token.
    """
    forms = []
    for match in re.finditer(r"<form\b(?P<attrs>[^>]*)>", source, re.IGNORECASE):
        attrs = match.group("attrs")
        method = re.search(r"method\s*=\s*[\"']?(\w+)[\"']?", attrs, re.IGNORECASE)
        end = source.lower().find("</form>", match.end())
        body = source[match.end() : end if end != -1 else len(source)]
        forms.append(
            {
                "method": (method.group(1) if method else "get").lower(),
                "line": source[: match.start()].count("\n") + 1,
                "has_csrf": "csrf_token" in body or "hidden_tag" in body,
            }
        )
    return forms


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    decorators: list[str]
    calls_abort: bool
    calls_flash: bool


def module_functions(source: str) -> list[FunctionInfo]:
    """Collect module-level functions with decorator names and certain calls."""
    tree = ast.parse(source)
    infos: list[FunctionInfo] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                target = decorator.func
            else:
                target = decorator
            if isinstance(target, ast.Name):
                decorators.append(target.id)
            elif isinstance(target, ast.Attribute):
                decorators.append(target.attr)
        calls = {
            child.func.id
            for child in ast.walk(node)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
        }
        infos.append(
            FunctionInfo(
                name=node.name,
                lineno=node.lineno,
                decorators=decorators,
                calls_abort="abort" in calls,
                calls_flash="flash" in calls,
            )
        )
    return infos


def route_decorators(source: str) -> list[tuple[str, str, list[str], bool]]:
    """Return ``(function, route_path, decorators, has_login_required)``."""
    tree = ast.parse(source)
    results = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names: list[str] = []
        route_path = ""
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(target, ast.Attribute):
                names.append(target.attr)
                if target.attr == "route" and isinstance(decorator, ast.Call) and decorator.args:
                    first = decorator.args[0]
                    if isinstance(first, ast.Constant):
                        route_path = str(first.value)
        if route_path:
            results.append((node.name, route_path, names, "login_required" in names))
    return results


def unused_imports(source: str) -> list[str]:
    """Module-level ``import x`` names that never appear elsewhere in the file."""
    tree = ast.parse(source)
    imported: list[tuple[str, int]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported.append((name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                imported.append((alias.asname or alias.name, node.lineno))

    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                used.add(current.id)

    # Names referenced from string annotations or __all__ still count as used.
    text = source
    return [
        f"line {lineno}: '{name}' is imported but unused"
        for name, lineno in imported
        if name not in used and not re.search(rf"['\"]{name}['\"]", text)
    ]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
