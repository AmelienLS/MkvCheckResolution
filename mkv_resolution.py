import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

QUALITY_BY_WIDTH = [
    (3840, "4K"),
    (2560, "2K"),
    (1920, "FHD"),
    (1280, "HD"),
    (0, "SD"),
]

def classify(width: int) -> str:
    for threshold, label in QUALITY_BY_WIDTH:
        if width >= threshold:
            return label
    return "Unknown"

def get_video_resolution(path: Path):
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
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        width, height = map(int, result.stdout.strip().split("x"))
        return width, height
    except Exception:
        return None, None


def main(initial_paths):
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

    def update_list(files):
        if not files:
            return
        for p in files:
            width, height = get_video_resolution(Path(p))
            if width is None:
                tree.insert("", tk.END, values=(Path(p).name, "Unknown", "-"))
            else:
                quality = classify(width)
                tree.insert(
                    "", tk.END, values=(Path(p).name, f"{width}x{height}", quality)
                )

    def select_files():
        files = filedialog.askopenfilenames(
            title="Select MKV files", filetypes=[("MKV Video", "*.mkv")]
        )
        update_list(files)

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
        root.after(0, lambda: update_list(initial_paths))

    root.mainloop()


def cli() -> None:
    """Entry point for console script."""
    main(sys.argv[1:])


if __name__ == "__main__":
    cli()
