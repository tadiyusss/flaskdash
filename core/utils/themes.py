from pathlib import Path
import subprocess
import sys

THEMES_DIR = Path(__file__).parent.parent.parent / 'themes'
STATIC_DIR = Path(__file__).parent.parent / 'static' / 'css' / 'themes'

def build_theme(theme_name: str):
    input_css = THEMES_DIR / f"{theme_name}.css"
    output_css = STATIC_DIR / f"{theme_name}.css"
    cwd = Path(__file__).parent.parent.parent
    tailwind = cwd / "node_modules" / ".bin" / "tailwindcss.cmd"

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

    print(f"Running command: {' '.join(command)} in {cwd}")
    
    subprocess.run(
        command,
        cwd=cwd
    )