import click
import os
from pathlib import Path
from core.utils.themes import build_theme


THEMES_DIR = Path(__file__).parent.parent.parent / 'themes'

@click.group('themes', help='Manage themes.')
def themes_group():
    """
    Group of commands for managing themes.
    """
    pass

@themes_group.command('list', help='List all available themes.')
def list_themes():
    if not THEMES_DIR.exists():
        os.makedirs(THEMES_DIR)

    themes = [f.name for f in THEMES_DIR.glob('*.css')]

    if themes:
        for theme in themes:
            click.echo(f"- {theme}")

@themes_group.command('build', help='Use the build command to compile and prepare themes for use.')
@click.option('--theme', prompt='Theme Name (without .css)', help='The name of the theme to build.')
def build_theme_command(theme):
    """
    Build and prepare themes for use.
    """ 
    
    try:
        build_theme(theme)
        click.echo(f"Theme '{theme}' built successfully.")
    except FileNotFoundError as e:
        click.echo(str(e))