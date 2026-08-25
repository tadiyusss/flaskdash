from flask_migrate import upgrade
from core.utils.registry.extensions import EXTENSIONS_LOCATION

def _validate_extension_migrations(extension_name):
    """
    Validate that migrations exist for an extension.
    :param extension_name: The name of the extension to validate.
    :return: Path to the migrations directory.
    """
    extension_path = EXTENSIONS_LOCATION / extension_name
    migrations_path = extension_path / "migrations"

    if not migrations_path.exists():
        raise FileNotFoundError(f"No migrations found for extension '{extension_name}'.")
    
    return migrations_path


def upgrade_extension_database(extension_name):
    """
    Run migrations for a specific extension.
    :param extension_name: The name of the extension to migrate.
    """
    migrations_path = _validate_extension_migrations(extension_name)
    upgrade(directory=str(migrations_path))


