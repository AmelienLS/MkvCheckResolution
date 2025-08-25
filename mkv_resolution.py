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
    messages = []
    for p in paths:
        width, height = get_video_resolution(Path(p))
        if width is None:
            messages.append(f"{Path(p).name}: unable to determine resolution")
        else:
            quality = classify(width)
            messages.append(f"{Path(p).name}: {width}x{height} ({quality})")
    return messages


def main(initial_paths):
    root = tk.Tk()
    root.title("MKV Resolution Checker")

    listbox = tk.Listbox(root, width=60)
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_list(files):
        if not files:
            return
        for msg in process(files):
            listbox.insert(tk.END, msg)

    def select_files():
        files = filedialog.askopenfilenames(
            title="Select MKV files", filetypes=[("MKV Video", "*.mkv")]
        )
        update_list(files)

    btn = ttk.Button(root, text="Select MKV Files", command=select_files)
    btn.pack(pady=(0, 10))

    if initial_paths:
        root.after(0, lambda: update_list(initial_paths))

    root.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
