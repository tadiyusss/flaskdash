import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

STUB_FILE_PATH = (
    Path(__file__).parent.parent
    / 'stubs'
    / 'extensions'
)

EXTENSIONS_PATH = (
    Path(__file__).parent.parent.parent 
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

@click.command('delete-extension', help='Delete an existing extension by name.')
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

    extension_slug_name = slug_case(name)
    extension_snake_name = snake_case(name)

    extension_path = EXTENSIONS_PATH / extension_snake_name

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
@click.command('create-extension', help='Open interactive menu to create a new extension.')
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
        'author_name': author
    }


    new_extension_path = EXTENSIONS_PATH / context['extension_snake_name']
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
    
