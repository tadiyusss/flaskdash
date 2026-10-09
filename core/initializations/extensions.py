import importlib
from pathlib import Path
from core.utils.registry.extensions import list_extensions, register_extension
from core.extensions import db
from flask import current_app


def include_extension(app, extension_name):
    current_app.logger.info(f"Including extension {extension_name} in the application.")
    extension = importlib.import_module(f"extensions.{extension_name}").init_extension(app, db)
    app.register_blueprint(extension)

def check_if_env_file_patched(extension_name):
    env_file = Path(f"extensions/{extension_name}/migrations/env.py")
    current_app.logger.debug(f"Checking if env.py for extension: {extension_name} is patched.")
    if not env_file.exists():
        return False

    content = env_file.read_text()
    return f'version_table="alembic_version_{extension_name}"' in content

def include_all_extensions(app):
    for extension in list_extensions():
        register_extension(extension)
        include_extension(app, extension)
        handle_extension_migrations(extension, app)


def handle_extension_migrations(extension_name, app):
    migration_path = Path(f"extensions/{extension_name}/migrations")

    with app.app_context():
        if migration_path.exists():
            # check if the "alembic_version_{extension_name}" exists in the env file
            if not check_if_env_file_patched(extension_name):
                patch_env_file(extension_name)



def patch_env_file(extension_name):
    current_app.logger.debug(f"Patching env.py for extension: {extension_name} to include version_table.")
    env_file = Path(f"extensions/{extension_name}/migrations/env.py")

    if not env_file.exists():
        current_app.logger.error(f"env.py for extension: {extension_name} does not exist.")
        return

    original = env_file.read_text()

    patched = original.replace(
        'context.configure(',
        f'context.configure(\n        version_table="alembic_version_{extension_name}",'
    )

    patched = "from core.extensions import db\ntarget_metadata = db.metadata\n" + patched
    patched = patched.replace("target_metadata = None", "")

    env_file.write_text(patched)
    current_app.logger.debug(f"Successfully patched env.py for extension: {extension_name}.")