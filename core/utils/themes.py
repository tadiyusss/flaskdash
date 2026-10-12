import os
from pathlib import Path
import subprocess
from core.defaults import THEMES_DIR, THEMES_OUTPUT_DIR
import json
from flask import current_app

class Theme:
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def build(self):
        input_css = self.path / "input.css"
        output_css = THEMES_OUTPUT_DIR / f"{self.name}.css"
        cwd = Path(__file__).parent.parent.parent

        if os.name == 'nt':
            tailwind = cwd / "node_modules" / ".bin" / "tailwindcss.cmd"
        else:
            tailwind = cwd / "node_modules" / ".bin" / "tailwindcss"

        output_css.parent.mkdir(parents=True, exist_ok=True)

        if not input_css.exists():
            raise FileNotFoundError(f"Theme '{self.name}' not found in {THEMES_DIR}")

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

    def info(self):
        theme_info_path = self.path / "theme.json"
        with open(theme_info_path, 'r') as f:
            return json.load(f)

    @property
    def is_valid(self):
        if not self.path.exists() or not self.path.is_dir():
            current_app.logger.warning(f"{self.path} is not a valid theme directory")
            return False

        input_file = self.path / "input.css"
        themes_metadata = self.path / "theme.json"

        if not input_file.exists() or not themes_metadata.exists():
            current_app.logger.warning(f"{self.path} is not a valid theme")
            return False
        current_app.logger.debug(f"{self.path} is a valid valid theme directory")
        return True

    def __repr__(self):
        return f"<Theme name={self.name} path={self.path}>"


