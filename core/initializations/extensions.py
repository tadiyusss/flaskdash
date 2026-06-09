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

    with app.app_context():
        if migration_path.exists():
            # check if patched
            if not (migration_path / "env.py").exists():
                print(f"Patched env.py not found for {extension_name}, patching now...")
                patch_env_file(extension_name)



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