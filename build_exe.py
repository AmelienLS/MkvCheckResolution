"""Helper script to build a standalone executable using PyInstaller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Invoke PyInstaller to build a single-file executable."""
    if shutil.which("pyinstaller") is None:
        sys.exit("PyInstaller must be installed (pip install pyinstaller).")

    script = Path(__file__).with_name("mkv_resolution.py")
    cmd: list[str] = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        "mkv_resolution",
        str(script),
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
