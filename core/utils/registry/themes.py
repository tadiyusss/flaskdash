from flask import current_app
from core.defaults import THEMES_DIR
from core.utils.themes import Theme

_registered_themes = list()

def register_theme(theme: Theme) -> bool:
    if not theme.is_valid:
        current_app.logger.warning(f"Theme '{theme.name}' is not valid and cannot be registered.")
        return False

    if theme.path in _registered_themes:
        current_app.logger.warning(f"Theme '{theme.name}' is already registered.")
        return False

    _registered_themes.append(theme)
    current_app.logger.info(f"Registered theme: {theme.name}")
    return True


def get_all_themes() -> list[Theme]:
    valid_themes = []

    if not THEMES_DIR.exists():
        THEMES_DIR.mkdir(parents=True)
    
    for theme_path in THEMES_DIR.iterdir():
        if not theme_path.is_dir():
            current_app.logger.warning(f"{theme_path} is not a directory and will be skipped.")
            continue

        theme = Theme(name=theme_path.name, path=theme_path)

        if not theme.is_valid:
            current_app.logger.warning(f"Theme '{theme.name}' is not valid and will be skipped.")
            continue

        valid_themes.append(theme)
    
    return valid_themes + _registered_themes

