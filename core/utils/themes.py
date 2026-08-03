import os
from pathlib import Path
import subprocess
import sys
from core.defaults import THEMES_DIR

STATIC_DIR = Path(__file__).parent.parent / 'static' / 'css' / 'themes'

def build_theme(theme_name: str):
    input_css = THEMES_DIR / theme_name / "input.css"
    output_css = STATIC_DIR / f"{theme_name}.css"
    cwd = Path(__file__).parent.parent.parent

    if os.name == 'nt':
        tailwind = cwd / "node_modules" / ".bin" / "tailwindcss.cmd"
    else:
        tailwind = cwd / "node_modules" / ".bin" / "tailwindcss"

    output_css.parent.mkdir(parents=True, exist_ok=True)

    if not input_css.exists():
        raise FileNotFoundError(f"Theme '{theme_name}' not found in {THEMES_DIR}")

    command = [
        str(tailwind),
        "-i",
        str(input_css),
        "-o",
        str(output_css)
    ]

    subprocess.run(
        command,
        cwd=cwd
    )

def list_themes():
    if not THEMES_DIR.exists():
        THEMES_DIR.mkdir(parents=True)

    folders_in_themes_dir = os.listdir(THEMES_DIR)
    for folder in folders_in_themes_dir:
        folder_path = THEMES_DIR / folder
        if folder_path.is_dir():
            input_file = folder_path / f"input.css"
            if input_file.exists():
                yield folder