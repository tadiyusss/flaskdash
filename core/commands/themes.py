import click
import os
from pathlib import Path
from core.utils.themes import build_theme, list_themes, get_theme_info
from core.defaults import THEMES_DIR

@click.group('themes', help='Manage themes.')
def themes_group():
    """
    Group of commands for managing themes.
    """
    pass

@themes_group.command('list', help='List all available themes.')
def list_themes_command():
    themes = list_themes()

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

@themes_group.command('view', help="View the information about the selected theme")
@click.option('--theme', prompt="Theme Name (without .css)", help="The name of the theme to view")
def view_theme_command(theme):
    """
    Show information about the theme selected
    """
    theme_info = get_theme_info(theme)
    for key in theme_info:
        if isinstance(theme_info[key], list):
            print(f"{key}: {', '.join(theme_info[key])}")
        else:
            print(f"{key}: {theme_info[key]}")