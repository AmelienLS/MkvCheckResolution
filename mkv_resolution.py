"""GUI application for inspecting MKV video metadata.

Uses ffprobe to extract resolution, codec, frame rate, audio and subtitle
languages and classifies the quality based on the width. A simple Tkinter
interface allows selecting multiple MKV files and displays these details in a
table.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

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


def get_video_metadata(path: Path) -> dict[str, Any]:
    """Retrieve various metadata of a video using ffprobe.

    The returned dictionary may contain the keys ``width``, ``height``,
    ``codec``, ``fps``, ``audio`` (list of ``lang (codec)`` strings) and
    ``subtitles`` (list of ``lang (codec)`` strings). Missing values are set
    to ``None`` or an empty list.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,avg_frame_rate,tags",
        "-of",
        "json",
        str(path),
    ]
    metadata: dict[str, Any] = {
        "width": None,
        "height": None,
        "codec": None,
        "fps": None,
        "audio": [],
        "subtitles": [],
    }
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError) as exc:
        logger.warning("Failed to probe %s: %s", path, exc)
        return metadata

    for stream in data.get("streams", []):
        stype = stream.get("codec_type")
        if stype == "video" and metadata["width"] is None:
            metadata["width"] = stream.get("width")
            metadata["height"] = stream.get("height")
            metadata["codec"] = stream.get("codec_name")
            rate = stream.get("avg_frame_rate")
            if rate and rate != "0/0":
                try:
                    num, den = map(int, rate.split("/"))
                    metadata["fps"] = f"{num/den:.3f}".rstrip("0").rstrip(".")
                except ValueError:
                    pass
        elif stype == "audio":
            tags = stream.get("tags", {})
            lang = tags.get("language", "und")
            codec = stream.get("codec_name")
            metadata["audio"].append(
                f"{lang} ({codec})" if codec else lang
            )
        elif stype == "subtitle":
            tags = stream.get("tags", {})
            lang = tags.get("language", "und")
            codec = stream.get("codec_name")
            metadata["subtitles"].append(
                f"{lang} ({codec})" if codec else lang
            )
    return metadata


def _update_list(tree: ttk.Treeview, files: Iterable[str]) -> None:
    """Populate the tree view with metadata info for each file."""
    for file_path in files:
        metadata = get_video_metadata(Path(file_path))
        width = metadata["width"]
        height = metadata["height"]
        if width is None or height is None:
            tree.insert(
                "",
                tk.END,
                values=(Path(file_path).name, "Unknown", "-", "-", "-", "-", "-"),
            )
            continue
        quality = classify(width)
        resolution = f"{width}x{height}"
        fps = metadata["fps"] or "-"
        codec = metadata["codec"] or "-"
        audio = ", ".join(metadata["audio"]) or "-"
        subs = ", ".join(metadata["subtitles"]) or "-"
        tree.insert(
            "",
            tk.END,
            values=(
                Path(file_path).name,
                resolution,
                fps,
                codec,
                audio,
                subs,
                quality,
            ),
        )


def build_ui(initial_paths: Iterable[str]) -> tk.Tk:
    """Create the Tkinter UI for the application."""
    root = tk.Tk()
    root.title("MKV Resolution Checker")

    style = ttk.Style(root)
    if sys.platform == "darwin" and "aqua" in style.theme_names():
        style.theme_use("aqua")

    columns = ("file", "resolution", "fps", "video", "audio", "subs", "quality")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("file", text="File")
    tree.heading("resolution", text="Resolution")
    tree.heading("fps", text="FPS")
    tree.heading("video", text="Video")
    tree.heading("audio", text="Audio")
    tree.heading("subs", text="Subtitles")
    tree.heading("quality", text="Quality")
    tree.column("file", width=300)
    tree.column("resolution", width=100, anchor=tk.CENTER)
    tree.column("fps", width=60, anchor=tk.CENTER)
    tree.column("video", width=100, anchor=tk.CENTER)
    tree.column("audio", width=150, anchor=tk.CENTER)
    tree.column("subs", width=150, anchor=tk.CENTER)
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
