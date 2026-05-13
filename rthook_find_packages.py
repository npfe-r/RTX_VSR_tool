"""Runtime hook: find system-installed Python packages (torch, nvvfx, etc.).

Adds the active Python's site-packages to sys.path so the bundled exe can
load large libraries (torch, nvvfx) that were excluded from the bundle.
"""
import sys
import subprocess
import os


def _find_site_packages() -> list[str]:
    found = []

    # 1) Try python.exe in PATH
    for exe in ["python", "python3", "py"]:
        try:
            r = subprocess.run(
                [exe, "-c", "import site, sys; print('\\n'.join(site.getsitepackages()))"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                for line in r.stdout.strip().splitlines():
                    p = line.strip()
                    if p and os.path.isdir(p):
                        found.append(p)
                if found:
                    break
        except Exception:
            continue

    # 2) Fallback: common Windows locations matching the current Python version
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    ver_flat = ver.replace(".", "")
    fallbacks = [
        os.path.expanduser(f"~/AppData/Roaming/Python/Python{ver_flat}/site-packages"),
        f"C:/Python{ver_flat}/Lib/site-packages",
        f"C:/Program Files/Python{ver_flat}/Lib/site-packages",
    ]
    for p in fallbacks:
        if p not in found and os.path.isdir(p):
            found.append(p)

    return found


_added = set()
for p in _find_site_packages():
    if p not in _added and p not in sys.path:
        sys.path.insert(0, p)
        _added.add(p)
