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

def process(paths):
    rows = []
    for p in paths:
        width, height = get_video_resolution(Path(p))
        if width is None:
            rows.append((Path(p).name, "N/A", "Unknown"))
        else:
            quality = classify(width)
            rows.append((Path(p).name, f"{width}x{height}", quality))
    return rows


def main(initial_paths):
    root = tk.Tk()
    root.title("MKV Resolution Checker")
    root.geometry("640x400")

    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("file", "resolution", "quality")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.heading("file", text="File")
    tree.heading("resolution", text="Resolution")
    tree.heading("quality", text="Quality")
    tree.column("file", width=360, anchor="w")
    tree.column("resolution", width=120, anchor="center")
    tree.column("quality", width=80, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_table(files):
        if not files:
            return
        for row in process(files):
            tree.insert("", tk.END, values=row)

    def select_files():
        files = filedialog.askopenfilenames(
            title="Select MKV files", filetypes=[("MKV Video", "*.mkv")]
        )
        update_table(files)

    btn = ttk.Button(root, text="Select MKV Files", command=select_files)
    btn.pack(pady=(0, 10))

    if initial_paths:
        root.after(0, lambda: update_table(initial_paths))

    root.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
