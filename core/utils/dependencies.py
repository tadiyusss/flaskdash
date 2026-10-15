import logging
import subprocess
import sys
from importlib import invalidate_caches
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from flask import current_app
from packaging.requirements import InvalidRequirement, Requirement

CORE_REQUIREMENTS = Path(__file__).parent.parent.parent / "requirements.txt"

def _read_requirements(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text().splitlines():
        line = raw.split(" #")[0].strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def _is_satisfied(line: str) -> bool:
    if line.startswith("-"):        
        return False
    try:
        req = Requirement(line)
    except InvalidRequirement:
        return False
    if req.marker and not req.marker.evaluate():
        return True                 
    try:
        installed = version(req.name)
    except PackageNotFoundError:
        return False
    return not req.specifier or req.specifier.contains(installed, prereleases=True)


def install_extension_requirements(extension_name: str, extensions_dir: Path) -> bool:

    req_file = extensions_dir / extension_name / "requirements.txt"
    if not req_file.exists():
        return True

    missing = [l for l in _read_requirements(req_file) if not _is_satisfied(l)]
    if not missing:
        return True

    current_app.logger.info("Installing dependencies for '%s': %s", extension_name, ", ".join(missing))

    cmd = [sys.executable, "-m", "pip", "install",
           "--disable-pip-version-check", "-r", str(req_file)]
  
    if CORE_REQUIREMENTS.exists():
        cmd += ["-c", str(CORE_REQUIREMENTS)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        current_app.logger.error("Timed out installing dependencies for '%s'", extension_name)
        return False

    if result.returncode != 0:
        current_app.logger.error("Dependency install failed for '%s':\n%s", extension_name, result.stderr)
        return False

    invalidate_caches() 
    return True