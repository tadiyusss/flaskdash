"""Unit tests for the click command groups registered by the app factory.

Commands are invoked through ``app.test_cli_runner()`` because Flask's CLI
group pushes an application context; a bare ``CliRunner`` does not, and several
commands touch ``current_app.logger``.
"""

from __future__ import annotations

import shutil

import pytest


pytestmark = pytest.mark.usefixtures("db_reset")


def run(app, *args, input=None):
    """Invoke the CLI inside an app context (needed by ``current_app.logger``)."""
    app.config.setdefault("TESTING", True)
    runner = app.test_cli_runner()
    with app.app_context():
        return runner.invoke(args=list(args), input=input)


class TestCommandRegistration:
    def test_top_level_help_lists_groups(self, app):
        result = run(app, "--help")
        assert result.exit_code == 0
        for group in ("extensions", "users", "themes"):
            assert group in result.output

    @pytest.mark.parametrize("group", ["extensions", "users", "themes"])
    def test_group_help(self, app, group):
        result = run(app, group, "--help")
        assert result.exit_code == 0

    def test_users_subcommands_present(self, app):
        result = run(app, "users", "--help")
        assert "create-admin" in result.output
        assert "delete-user" in result.output

    def test_themes_subcommands_present(self, app):
        result = run(app, "themes", "--help")
        for command in ("list", "build", "view"):
            assert command in result.output

    def test_extensions_subcommands_present(self, app):
        result = run(app, "extensions", "--help")
        for command in ("create", "delete", "makemigration", "install-deps", "upgrade"):
            assert command in result.output


class TestThemeCommands:
    def test_list_reports_available_themes(self, app):
        result = run(app, "themes", "list")
        assert result.exit_code == 0, result.output
        assert "default" in result.output

    def test_view_prints_metadata(self, app):
        result = run(app, "themes", "view", "--theme", "default")
        assert result.exit_code == 0, result.output
        assert "Information for theme 'default'" in result.output

    def test_view_unknown_theme_reports_not_found(self, app):
        result = run(app, "themes", "view", "--theme", "nope")
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_build_unknown_theme_reports_not_found(self, app):
        result = run(app, "themes", "build", "--theme", "nope")
        assert result.exit_code == 0
        assert "not found" in result.output


class TestUserCommands:
    def test_delete_missing_user_reports_not_found(self, app):
        result = run(app, "users", "delete-user", "--username", "ghost")
        assert "deleted successfully" not in result.output


class TestExtensionCommands:
    def test_create_generates_expected_files(self, app, tmp_path, monkeypatch):
        import core.commands.extensions as extensions_command

        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", tmp_path)

        result = run(app, "extensions", "create", input="Contact Box\nAUTHOR\n")

        created = tmp_path / "contact_box"
        assert result.exit_code == 0, result.output
        assert created.is_dir()
        assert (created / "metadata.py").is_file()
        assert (created / "__init__.py").is_file()
        assert "created successfully" in result.output

    def test_create_slugifies_names(self, app, tmp_path, monkeypatch):
        import core.commands.extensions as extensions_command

        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", tmp_path)

        run(app, "extensions", "create", input="My Cool Thing\nAUTHOR\n")

        assert (tmp_path / "my_cool_thing").is_dir()

    def test_create_does_not_sanitise_path_separators(self, app, tmp_path, monkeypatch):
        """Security finding: ``create`` joins the raw name into the target path.

        ``snake_case`` only lowercases and swaps spaces, so ``../`` survives and
        the generated extension is written *outside* ``EXTENSIONS_LOCATION``.
        Asserted as the current behaviour so a fix flips this test.
        """
        import core.commands.extensions as extensions_command

        sandbox = tmp_path / "extensions"
        sandbox.mkdir()
        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", sandbox)

        escaped = tmp_path / "escaped"
        try:
            result = run(app, "extensions", "create", input="../escaped\nAUTHOR\n")
            assert result.exit_code == 0, result.output
            assert escaped.is_dir(), "expected the traversal to escape the extensions root"
        finally:
            shutil.rmtree(escaped, ignore_errors=True)

    def test_delete_missing_extension_reports_not_found(self, app, tmp_path, monkeypatch):
        import core.commands.extensions as extensions_command

        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", tmp_path)
        result = run(app, "extensions", "delete", "--name", "ghost", input="y\n")
        assert "not found" in result.output

    def test_delete_requires_confirmation(self, app, tmp_path, monkeypatch):
        import core.commands.extensions as extensions_command

        target = tmp_path / "doomed"
        target.mkdir()
        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", tmp_path)

        result = run(app, "extensions", "delete", "--name", "doomed", input="n\n")

        assert "Deletion cancelled" in result.output
        assert target.is_dir()

    def test_install_deps_with_no_extensions_is_a_noop(self, app, tmp_path, monkeypatch):
        import core.commands.extensions as extensions_command

        monkeypatch.setattr(extensions_command, "EXTENSIONS_LOCATION", tmp_path)
        result = run(app, "extensions", "install-deps")
        assert result.exit_code == 0, result.output
