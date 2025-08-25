# MkvCheckResolution

A quick cross-platform GUI application to batch check the resolution of `.mkv` files.
The main window shows a table listing each file with its resolution and quality tier (4K, 2K, FHD, HD, SD).

## Requirements
- Python 3
- [`ffprobe`](https://ffmpeg.org/ffprobe.html) from the FFmpeg suite must be available in your PATH.

## Usage

Double-click the script or run it from a terminal:

```bash
python mkv_resolution.py
```

Use the **Select MKV Files** button to choose one or more videos and their information appears in the table.
Dragging `.mkv` files onto the application icon (or passing file paths on the command line) will populate the table automatically when the app opens.

## Build

To create a standalone executable for Windows or macOS, install [PyInstaller](https://pyinstaller.org/) and run the build script:

```bash
pip install pyinstaller
python build.py
```

The resulting executable in the `dist/` folder accepts drag-and-drop of `.mkv` files on both platforms.
