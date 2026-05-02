from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "Audly"
COLLECT_PACKAGES = ("yt_dlp", "certifi", "imageio_ffmpeg")
ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
RELEASE_DIR = ROOT / "release"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print(" ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def current_platform() -> str:
    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    raise SystemExit(f"Unsupported release platform: {system}")


def ensure_windows_icon() -> Path:
    icon_path = ROOT / "matcha.ico"
    if icon_path.exists():
        return icon_path

    from PIL import Image

    source = ROOT / "matchaicon.png"
    image = Image.open(source)
    image.save(
        icon_path,
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    return icon_path


def icon_for(platform_name: str) -> Path:
    if platform_name == "windows":
        return ensure_windows_icon()
    return ROOT / "matcha.icns"


def pyinstaller_args(platform_name: str) -> list[str]:
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--windowed",
        "--onedir",
        "--name",
        APP_NAME,
        "--icon",
        str(icon_for(platform_name)),
    ]

    for package in COLLECT_PACKAGES:
        args.extend(["--collect-all", package])

    args.append(str(ROOT / "audly.py"))
    return args


def build(platform_name: str) -> None:
    run(pyinstaller_args(platform_name))


def package(platform_name: str) -> Path:
    RELEASE_DIR.mkdir(exist_ok=True)

    if platform_name == "windows":
        source_dir = DIST_DIR / APP_NAME
        archive_base = RELEASE_DIR / "Audly-Windows"
        zip_path = Path(shutil.make_archive(str(archive_base), "zip", source_dir))
        return zip_path

    app_path = DIST_DIR / f"{APP_NAME}.app"
    zip_path = RELEASE_DIR / "Audly-macOS.zip"
    run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app_path), str(zip_path)])
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and package Audly for the current OS.")
    parser.add_argument(
        "--package",
        action="store_true",
        help="Create a release zip after the PyInstaller build succeeds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    platform_name = current_platform()

    build(platform_name)

    if args.package:
        zip_path = package(platform_name)
        print(f"Created release archive: {zip_path}")


if __name__ == "__main__":
    main()
