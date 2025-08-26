"""GUI application for checking MKV video resolutions.

Uses ffprobe to extract width and height from videos and classifies the quality
based on the width. A simple Tkinter interface allows selecting multiple MKV
files and displays their resolution and an estimated quality label.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import tkinter as tk
from tkinter import filedialog, ttk

logger = logging.getLogger(__name__)

QUALITY_BY_WIDTH: list[tuple[int, str]] = [
    (3840, "4K"),
    (2560, "2K"),
    (1920, "FHD"),
    (1280, "HD"),
    (0, "SD"),
]


def classify(width: int) -> str:
    """Return a quality label for the given width."""
    for threshold, label in QUALITY_BY_WIDTH:
        if width >= threshold:
            return label
    return "Unknown"


def get_video_resolution(path: Path) -> tuple[int | None, int | None]:
    """Retrieve the width and height of a video using ffprobe.

    Returns a tuple of integers if successful. On failure, ``(None, None)``
    is returned and a warning is logged.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split("x"))
        return width, height
    except (subprocess.SubprocessError, ValueError, FileNotFoundError) as exc:
        logger.warning("Failed to probe %s: %s", path, exc)
        return None, None


def _update_list(tree: ttk.Treeview, files: Iterable[str]) -> None:
    """Populate the tree view with resolution info for each file."""
    for file_path in files:
        width, height = get_video_resolution(Path(file_path))
        if width is None:
            tree.insert("", tk.END, values=(Path(file_path).name, "Unknown", "-"))
            continue
        quality = classify(width)
        tree.insert(
            "", tk.END, values=(Path(file_path).name, f"{width}x{height}", quality)
        )


def build_ui(initial_paths: Iterable[str]) -> tk.Tk:
    """Create the Tkinter UI for the application."""
    root = tk.Tk()
    root.title("MKV Resolution Checker")

    style = ttk.Style(root)
    if sys.platform == "darwin" and "aqua" in style.theme_names():
        style.theme_use("aqua")

    columns = ("file", "resolution", "quality")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("file", text="File")
    tree.heading("resolution", text="Resolution")
    tree.heading("quality", text="Quality")
    tree.column("file", width=300)
    tree.column("resolution", width=100, anchor=tk.CENTER)
    tree.column("quality", width=80, anchor=tk.CENTER)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def select_files() -> None:
        files = filedialog.askopenfilenames(
            title="Select MKV files", filetypes=[("MKV Video", "*.mkv")]
        )
        _update_list(tree, files)

    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    open_accel = "Cmd+O" if sys.platform == "darwin" else "Ctrl+O"
    quit_accel = "Cmd+Q" if sys.platform == "darwin" else "Ctrl+Q"
    file_menu.add_command(label="Open…", command=select_files, accelerator=open_accel)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit, accelerator=quit_accel)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    if sys.platform == "darwin":
        root.bind_all("<Command-o>", lambda _e: select_files())
        root.bind_all("<Command-q>", lambda _e: root.quit())
    else:
        root.bind_all("<Control-o>", lambda _e: select_files())
        root.bind_all("<Control-q>", lambda _e: root.quit())

    if initial_paths:
        root.after(0, lambda: _update_list(tree, initial_paths))

    return root


def main(initial_paths: Iterable[str]) -> None:
    """Run the GUI application."""
    root = build_ui(initial_paths)
    root.mainloop()


def cli() -> None:
    """Entry point for console script."""
    logging.basicConfig(level=logging.WARNING)
    main(sys.argv[1:])


if __name__ == "__main__":
    cli()
