import subprocess
import sys
from pathlib import Path

from packaging.requirements import Requirement, InvalidRequirement
from packaging.utils import canonicalize_name
from importlib.metadata import distributions

# What's actually installed: {normalized_name: version}
installed = {
    canonicalize_name(d.metadata["Name"]): d.version for d in distributions()
}

# What requirements.txt asks for
required = {}
for line in Path("requirements.txt").read_text().splitlines():
    line = line.split("#")[0].strip()
    if not line or line.startswith("-"):
        continue
    try:
        req = Requirement(line)
    except InvalidRequirement:
        print(f"SKIPPED (can't parse): {line}")
        continue
    required[canonicalize_name(req.name)] = req

missing, mismatched = [], []
for name, req in required.items():
    if name not in installed:
        missing.append(str(req))
    elif req.specifier and not req.specifier.contains(installed[name], prereleases=True):
        mismatched.append(f"{req}  (installed: {installed[name]})")

extra = sorted(set(installed) - set(required))

print("\nMissing (in requirements.txt, not installed):")
print(*(missing or ["none"]), sep="\n  ")
print("\nVersion mismatch:")
print(*(mismatched or ["none"]), sep="\n  ")
print("\nInstalled but not in requirements.txt:")
print(*(extra or ["none"]), sep="\n  ")