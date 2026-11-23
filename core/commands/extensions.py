import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from core.utils.extensions import upgrade_extension_database, get_current_db_version
from core.utils.registry.extensions import EXTENSIONS_LOCATION, list_extensions
from flask_migrate import init, migrate
from core.initializations.extensions import patch_env_file, check_if_env_file_patched
from core.utils.dependencies import install_extension_requirements

STUB_FILE_PATH = (
    Path(__file__).parent.parent
    / 'stubs'
    / 'extensions'
)


def snake_case(text):
    return text.lower().replace(' ', '_')

def slug_case(text):
    return text.lower().replace(' ', '-')

def render_stub(stub_file_location, context):
    """
    Render a stub file with the given context and write it to the output file location.
    :stub_file_location: The relative path of the stub file to render. (ex: templates/my_template.html.stub)
    :context: The context to use for rendering the stub. (ex: {'variable_name': 'value'})
    """
    
    env = Environment(loader=FileSystemLoader(STUB_FILE_PATH))
    template = env.get_template(stub_file_location)
    return template.render(context)

@click.group('extensions', help='Manage extensions.')
def extensions_group():
    """
    Group of commands for managing extensions.
    """

@extensions_group.command('upgrade', help='Run migrations for a specific extension.')
@click.option('--extension', '-e', prompt='Extension Name', help='The name of the extension to migrate.')
def handle_upgrade_extension(extension):
    """
    Run migrations for a specific extension.
    :name: The name of the extension to migrate.
    """

    upgrade_extension_database(extension)    
    click.echo(f"Migrations for extension '{extension}' completed successfully.")

@extensions_group.command('current-db', help='Show the current database version for a specific extension.')
@click.option('--extension', '-e', prompt='Extension Name', help='The name of the extension to check.')
def handle_current_db_extension(extension):
    """
    Show the current database version for a specific extension.
    :name: The name of the extension to check.
    """
    get_current_db_version(extension)

@extensions_group.command('upgrade-all', help='Run migrations for all extensions.')
def handle_upgrade_all_extensions():
    for extension_path in EXTENSIONS_LOCATION.iterdir():
        if extension_path.is_dir():
            extension_name = extension_path.name
            click.echo(f"Running migrations for extension: {extension_name}")
            upgrade_extension_database(extension_name)
    click.echo("Migrations for all extensions completed successfully.")

@extensions_group.command('delete', help='Delete an existing extension by name.')
@click.option('--name', prompt='Extension Name', help='The name of the extension to delete.')
def delete_extension(name):
    """
    Delete an existing extension by name.
    :name: The name of the extension to delete.
    """
    confirmation = click.confirm(f"Are you sure you want to delete the extension '{name}'? This action cannot be undone.", default=False)
    
    if not confirmation:
        click.echo("Deletion cancelled.")
        return

    extension_snake_name = snake_case(name)

    extension_path = EXTENSIONS_LOCATION / extension_snake_name

    if not extension_path.exists():
        click.echo(f"Extension '{name}' not found.")
        return

    # Remove the extension directory and its contents
    for child in extension_path.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            for sub_child in child.glob('*'):
                sub_child.unlink()
            child.rmdir()
    extension_path.rmdir()

    click.echo(f"Extension '{name}' deleted successfully.")

@extensions_group.command('create', help='Open interactive menu to create a new extension.')
@click.option('--name', prompt='Extension Name', help='The name of the new extension.')
@click.option('--author', prompt='Author Name', help='The name of the author.')
def create_extension(name, author):
    """
    Open interactive menu to create a new extension and generate extension template
    """

    context = {
        'extension_name': name,
        'extension_slug_name': slug_case(name),
        'extension_snake_name': snake_case(name),
        'author': author
    }


    new_extension_path = EXTENSIONS_LOCATION / context['extension_snake_name']
    new_extension_path.mkdir(parents=True, exist_ok=True)

    for path in STUB_FILE_PATH.rglob('*'):
        relative_path = path.relative_to(STUB_FILE_PATH)
        if path.is_file():
            rendered_content = render_stub(relative_path.as_posix(), context)

            output_file_path = new_extension_path / relative_path
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file_path, 'w') as f:
                f.write(rendered_content)
            
            output_file_path.rename(output_file_path.with_suffix(''))

    click.echo(f"Extension '{name}' created successfully at '{new_extension_path}'.")
    click.echo(f"You may visit http://localhost:8000/{context['extension_slug_name']} to check the extension after running the server.")

    
@extensions_group.command('makemigration', help='Create a migration file for a specific extension.')
@click.option('--extension', '-e', prompt='Extension Name', help='The name of the extension.')
@click.option('--message', '-m', help='Short description of the change.')
def handle_make_migration(extension, message):

    extension_name = snake_case(extension)
    extension_path = EXTENSIONS_LOCATION / extension_name

    if not extension_path.is_dir():
        click.echo(f"Extension '{extension}' not found.")
        return

    migrations_path = extension_path / 'migrations'

    if not migrations_path.exists():
        init(directory=str(migrations_path))
        click.echo(f"Initialized migrations for '{extension_name}'.")

    if not check_if_env_file_patched(extension_name):
        patch_env_file(extension_name)

    versions_path = migrations_path / 'versions'
    versions_path.mkdir(exist_ok=True)
    existing = set(versions_path.glob('*.py'))

    migrate(directory=str(migrations_path), message=message)

    created = set(versions_path.glob('*.py')) - existing
    if created:
        for file in created:
            click.echo(f"Migration created: {file}")
    else:
        click.echo("No changes detected, no migration file was created.")

@extensions_group.command('install-deps', help='Install requirements for all extensions.')
def handle_install_deps():
    for ext in list_extensions():
        ok = install_extension_requirements(ext, EXTENSIONS_LOCATION)
        click.echo(f"{ext}: {'ok' if ok else 'FAILED'}")