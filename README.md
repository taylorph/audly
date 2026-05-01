# Audly

A polished desktop GUI for downloading and clipping media with yt-dlp and FFmpeg without writing terminal commands.

Audly wraps common `yt-dlp` workflows in a clean PySide6 interface for users who want MP3/MP4 downloads, clipping, output-folder selection, and progress feedback from a native desktop app.

![Audly desktop app screenshot](assets/audly-screenshot.png)

## Download

Download the latest public build from the Audly Releases page:

[Download Audly from GitHub Releases](https://github.com/taylorph/audly/releases/latest)

Choose the file for your operating system:

- macOS: download `Audly-macOS.zip`, unzip it, then open `audly.app`.
- Windows: download `Audly-Windows.zip`, unzip it, then run `Audly.exe`.

On macOS, Audly is currently unsigned. If macOS blocks the app on first launch, right click the app and choose Open.

## Features

- MP3 / MP4 downloads
- Preview metadata before downloading
- Custom output names with automatic `name (1)` copies
- Remembered output folder through application settings
- Best / Standard quality options
- Clip timestamps for partial downloads
- Output folder selection
- Real-time progress and debug log UI
- Dedicated success/failure result panel
- Product-safe activity log without raw dependency paths
- Bundled FFmpeg fallback through `imageio-ffmpeg`

## Tech Stack

- Python
- PySide6
- yt-dlp
- FFmpeg
- PyInstaller

## Resume-Ready Project Bullets

- Built a polished macOS desktop GUI for media downloading and clipping using Python, PySide6, yt-dlp, and FFmpeg.
- Implemented threaded downloads with real-time progress updates using QThread to maintain UI responsiveness.
- Designed a system that dynamically generates yt-dlp CLI commands based on user input.
- Packaged the application into native executables (.app and .exe) using PyInstaller.

## How It Works

Audly converts form input into structured `yt-dlp` options. The GUI collects the media URL, output folder, target format, quality level, and optional start/end timestamps, then passes those options to the yt-dlp Python API.

Preview and download work run in background `QThread` workers. Preview fetches metadata before downloading so users can confirm the title, uploader, duration, format, and thumbnail URL. Downloads use yt-dlp progress hooks to update the progress bar, status text, and in-app debug panel.

The result is a desktop wrapper around yt-dlp where users interact with buttons and fields while Audly shows live progress, errors, and the final saved file path inside the app.

## Project Structure

- `audly.py` starts the Qt app and opens the main window.
- `models.py` defines the typed request and metadata objects shared across the app.
- `workers.py` owns background `QThread` work for preview and download.
- `ui/` contains the main window, preview panel, progress panel, debug panel, and stylesheet.
- `ui/result_panel.py` shows unmistakable completion and failure states.
- `services/metadata_service.py` fetches preview metadata through yt-dlp.
- `services/download_service.py` owns download orchestration, FFmpeg preflight checks, and progress hooks.
- `services/file_naming_service.py` owns safe filenames and `name (1)` copy behavior.
- `services/ffmpeg_service.py` resolves bundled, system, or `imageio-ffmpeg` FFmpeg.
- `services/settings_service.py` persists the selected output folder with Qt settings.
- `services/ytdlp_options.py` keeps extractor options centralized.
- `services/ytdlp_logger.py` adapts yt-dlp logs into Audly's debug panel.

## Platform Support

- macOS native app bundle (`.app`)
- Windows executable (`.exe`)

## Requirements

- Python 3.10+
- Python dependencies from `requirements.txt`

Audly includes an `imageio-ffmpeg` fallback for packaged builds, and can also use a bundled `ffmpeg.exe` or system FFmpeg when available.

## Installation (Development)

```bash
python -m pip install -r requirements.txt
python audly.py
```

## Build Instructions

### macOS

```bash
pyinstaller --windowed --icon=matcha.icns audly.py
```

### Windows

Generate `matcha.ico` from `matchaicon.png` before building:

```bash
python -m pip install pillow
python -c "from PIL import Image; img = Image.open('matchaicon.png'); img.save('matcha.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```

Then build the folder-based Windows app:

```bash
pyinstaller --clean --noconfirm --windowed --onedir --name Audly --icon=matcha.ico --collect-all yt_dlp --collect-all certifi --collect-all imageio_ffmpeg audly.py
```

## Release Instructions

Releases are published through GitHub Releases:

[https://github.com/taylorph/audly/releases](https://github.com/taylorph/audly/releases)

To publish a new release, create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build both platforms and attach these files to the release:

- `Audly-macOS.zip`
- `Audly-Windows.zip`

For manual packaging, create release archives from the PyInstaller output:

```bash
zip -r Audly-macOS.zip dist/audly.app
Compress-Archive -Path dist\Audly\* -DestinationPath Audly-Windows.zip -Force
```

## Automated Builds

GitHub Actions builds Audly on both `macos-latest` and `windows-latest` for every push and version tag. Normal pushes upload build artifacts for verification. Version tags create release-ready zip files and attach them to GitHub Releases, so a Windows machine is not required to produce the Windows release build.

## License

MIT License. See `LICENSE` for details.
