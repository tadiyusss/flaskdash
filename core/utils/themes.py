import os
from pathlib import Path
import subprocess
import sys
from core.defaults import THEMES_DIR, THEMES_OUTPUT_DIR
import json

def build_theme(theme_name: str):
    input_css = THEMES_DIR / theme_name / "input.css"
    output_css = THEMES_OUTPUT_DIR / f"{theme_name}.css"
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

            input_file = folder_path / "input.css"
            themes_metadata = folder_path / "theme.json"

            if input_file.exists() and themes_metadata.exists():
                yield folder

def get_theme_info(theme_name):
    if theme_name not in list_themes():
        raise FileNotFoundError(f"Theme '{theme_name}' not found in {THEMES_DIR}")
    
    theme_info_path = THEMES_DIR / theme_name / "theme.json"
    with open(theme_info_path, 'r') as f:
        return json.load(f) 


