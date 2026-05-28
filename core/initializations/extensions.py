import importlib
import logging
from flask_migrate import upgrade, init, migrate, stamp
from pathlib import Path
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from core.utils.registry.extensions import list_extensions, register_extension
from core.extensions import db

logger = logging.getLogger(__name__)


def include_extension(app, extension_name):
    extension = importlib.import_module(f"extensions.{extension_name}").init_extension(app, db)
    app.register_blueprint(extension)


def include_all_extensions(app):
    for extension in list_extensions():
        register_extension(extension)
        include_extension(app, extension)
        handle_extension_migrations(extension, app)


def handle_extension_migrations(extension_name, app):
    migration_path = Path(f"extensions/{extension_name}/migrations")
    versions_path = migration_path / "versions"

    with app.app_context():
        if not migration_path.exists():
            initialize_extension_migrations(extension_name)
            patch_env_file(extension_name)

        if not versions_path.exists() or not any(versions_path.iterdir()):
            try:
                migrate(
                    directory=str(migration_path),
                    message=f"initial migration for {extension_name}"
                )
            except SystemExit:
                logger.info(f"[{extension_name}] No models to migrate")

            upgrade_extension(extension_name, app)
            return

        upgrade_extension(extension_name, app)

        if has_schema_changes(extension_name, app):
            try:
                migrate(
                    directory=str(migration_path),
                    message=f"auto migration for {extension_name}"
                )
                upgrade_extension(extension_name, app)
            except SystemExit:
                pass
            except Exception as e:
                logger.error(f"[{extension_name}] Migration error: {e}")
                raise


def has_schema_changes(extension_name, app) -> bool:
    migration_path = Path(f"extensions/{extension_name}/migrations")

    alembic_cfg = AlembicConfig()
    alembic_cfg.set_main_option("script_location", str(migration_path))
    alembic_cfg.set_main_option("version_table", f"alembic_version_{extension_name}")

    with app.app_context():
        with db.engine.connect() as conn:
            context = MigrationContext.configure(
                conn,
                opts={"version_table": f"alembic_version_{extension_name}"}
            )
            diff = compare_metadata(context, db.metadata)

    return bool(diff)


def upgrade_extension(extension_name, app):
    migration_path = Path(f"extensions/{extension_name}/migrations")

    with app.app_context():
        try:
            upgrade(directory=str(migration_path))
        except Exception as e:
            if "can't locate revision" in str(e).lower():
                logger.warning(f"[{extension_name}] Broken revision detected, stamping head")
                stamp(directory=str(migration_path), revision="head")
                upgrade(directory=str(migration_path))
            else:
                raise


def patch_env_file(extension_name):
    env_file = Path(f"extensions/{extension_name}/migrations/env.py")

    if not env_file.exists():
        return

    original = env_file.read_text()

    patched = original.replace(
        'context.configure(',
        f'context.configure(\n        version_table="alembic_version_{extension_name}",'
    )

    patched = "from core.extensions import db\ntarget_metadata = db.metadata\n" + patched
    patched = patched.replace("target_metadata = None", "")

    env_file.write_text(patched)


def initialize_extension_migrations(extension_name):
    migration_directory = Path(f"extensions/{extension_name}/migrations")

    if not migration_directory.exists():
        init(directory=str(migration_directory))