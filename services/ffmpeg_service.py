import shutil
import sys
from pathlib import Path


def resolve_ffmpeg_location() -> str:
    bundled = _bundled_ffmpeg()
    if bundled:
        return bundled

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ""


def _bundled_ffmpeg() -> str:
    root = _app_root()
    candidates = [
        root / "ffmpeg.exe",
        root / "ffmpeg" / "ffmpeg.exe",
        root / "tools" / "ffmpeg.exe",
        root / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return ""


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[1]
