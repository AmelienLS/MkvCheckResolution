# MkvCheckResolution

A quick cross-platform GUI application to inspect `.mkv` files.
It opens a table where each file's resolution, quality (4K, 2K, FHD, HD, SD),
frame rate, video codec, and audio and subtitle track languages are listed and
includes a standard **File** menu for a more native macOS feel.

## Requirements
- Python 3
- [`ffprobe`](https://ffmpeg.org/ffprobe.html) from the FFmpeg suite must be available in your PATH.

## Installation

Clone or download this repository, open a terminal in the project directory, and install the package:

```bash
git clone https://github.com/Unknown/MkvCheckResolution.git
cd MkvCheckResolution
pip install -e .
```

## Usage

Run via the installed command:

```bash
mkv-resolution [files...]
```

or invoke the script directly:

```bash
python mkv_resolution.py [files...]
```

You can also install directly from Git without cloning by running:

```bash
pip install git+https://github.com/Unknown/MkvCheckResolution.git
```

If no file paths are provided, a window opens with a **Select MKV Files** button and a **File → Open…** menu item to choose one or more videos.
You can also drag and drop `.mkv` files onto the application icon (or provide
file paths as command line arguments) and the window will display their
resolutions, frame rate, codecs, and audio/subtitle languages.

## Build

To create a source distribution and wheel, first install the `build` package and run:

```bash
pip install build
python -m build
```

To produce a standalone executable for Windows or macOS, install [PyInstaller](https://pyinstaller.org/) and run the build script:

```bash
pip install pyinstaller
python build_exe.py
```

The resulting executable in the `dist/` folder accepts drag-and-drop of `.mkv` files on both platforms.
On macOS the generated `.app` can be launched by double-clicking, allowing use without the command line.
