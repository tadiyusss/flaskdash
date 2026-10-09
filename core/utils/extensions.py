from flask_migrate import upgrade
from core.utils.registry.extensions import EXTENSIONS_LOCATION
from flask import current_app


def _validate_extension_migrations(extension_name):
    """
    Validate that migrations exist for an extension.
    :param extension_name: The name of the extension to validate.
    :return: Path to the migrations directory.
    """
    extension_path = EXTENSIONS_LOCATION / extension_name
    migrations_path = extension_path / "migrations"

    if not migrations_path.exists():
        current_app.logger.error(f"No migrations found for extension '{extension_name}'.")
        return None
    
    return migrations_path


def upgrade_extension_database(extension_name):
    """
    Run migrations for a specific extension.
    :param extension_name: The name of the extension to migrate.
    """
    migrations_path = _validate_extension_migrations(extension_name)
    if migrations_path is None:
        current_app.logger.error(f"Cannot run migrations for extension '{extension_name}' as no migrations were found.")
        return
    upgrade(directory=str(migrations_path))


