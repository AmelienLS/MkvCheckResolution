import subprocess
import shutil
import sys
from pathlib import Path

"""Build a standalone executable using PyInstaller."""

def main() -> None:
    if shutil.which("pyinstaller") is None:
        sys.exit("PyInstaller must be installed (pip install pyinstaller).")
    script = Path(__file__).parent / "mkv_resolution.py"
    cmd = [
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
