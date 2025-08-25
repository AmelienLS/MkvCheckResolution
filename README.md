# MkvCheckResolution

A quick cross-platform GUI application to batch check the resolution of `.mkv` files.
It opens a small window where each file and its resolution quality (4K, 2K, FHD, HD, SD) is listed.

## Requirements
- Python 3
- [`ffprobe`](https://ffmpeg.org/ffprobe.html) from the FFmpeg suite must be available in your PATH.

## Usage

Run the script directly:

```bash
python mkv_resolution.py [files...]
```

If no file paths are provided, a window opens with a **Select MKV Files** button to choose one or more videos.
You can also drag and drop `.mkv` files onto the application icon (or provide file paths as command line arguments) and the window will display their resolutions.

## Build

To create a standalone executable for Windows or macOS, install [PyInstaller](https://pyinstaller.org/) and run the build script:

```bash
pip install pyinstaller
python build.py
```

The resulting executable in the `dist/` folder accepts drag-and-drop of `.mkv` files on both platforms.
