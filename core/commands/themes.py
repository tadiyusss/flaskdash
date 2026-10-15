import click
from core.utils.registry.themes import get_all_themes

@click.group('themes', help='Manage themes.')
def themes_group():
    """
    Group of commands for managing themes.
    """
    pass

@themes_group.command('list', help='List all available themes.')
def get_all_themes_command():
    themes = get_all_themes()
    
    if not themes:
        click.echo("No themes found.")
        return

    click.echo("Available themes:")
    for theme in themes:
        click.echo(f"- {theme.name}")

@themes_group.command('build', help='Use the build command to compile and prepare themes for use.')
@click.option('--theme', prompt='Theme Name (without .css)', help='The name of the theme to build.')
def build_theme_command(theme):
    """
    Build and prepare themes for use.
    """ 
    themes = get_all_themes()
    theme_names = [t.name for t in themes]

    if theme not in theme_names:
        click.echo(f"Theme '{theme}' not found.")
        return

    theme_obj = next(t for t in themes if t.name == theme)
    try:
        theme_obj.build()
        click.echo(f"Theme '{theme}' built successfully.")
    except Exception as e:
        click.echo(f"Error building theme '{theme}': {e}")

@themes_group.command('view', help="View the information about the selected theme")
@click.option('--theme', prompt="Theme Name (without .css)", help="The name of the theme to view")
def view_theme_command(theme):
    """
    Show information about the theme selected
    """
    themes = get_all_themes()
    theme_names = [t.name for t in themes]

    if theme not in theme_names:
        click.echo(f"Theme '{theme}' not found.")
        return

    theme_obj = next(t for t in themes if t.name == theme)
    try:
        info = theme_obj.info()
        click.echo(f"Information for theme '{theme}':")
        for key, value in info.items():
            click.echo(f"{key}: {value}")
    except Exception as e:
        click.echo(f"Error retrieving information for theme '{theme}': {e}")