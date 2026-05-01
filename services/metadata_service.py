from typing import Any
from urllib.request import Request, urlopen

import yt_dlp

from models import MediaMetadata
from services.ffmpeg_service import resolve_ffmpeg_location
from services.ytdlp_options import YOUTUBE_EXTRACTOR_ARGS


def format_duration(seconds: Any) -> str:
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        return "Unknown"

    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"

    return f"{minutes}:{secs:02d}"


def fetch_metadata(
    url: str,
    media_format: str,
    quality: str,
    allow_playlist: bool = False,
    logger=None,
) -> MediaMetadata:
    ffmpeg_location = resolve_ffmpeg_location()
    if logger and ffmpeg_location:
        logger.debug("FFmpeg ready.")
    elif logger:
        logger.warning("FFmpeg was not found. MP3 conversion, merging, and clips may fail.")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": not allow_playlist,
        "extractor_args": YOUTUBE_EXTRACTOR_ARGS,
        "logger": logger,
    }

    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    selected_format = _describe_selected_format(info, media_format, quality)
    is_playlist = info.get("_type") == "playlist"
    entry_count = _entry_count(info)
    first_entry = _first_entry(info) if is_playlist else {}

    thumbnail_url = info.get("thumbnail") or first_entry.get("thumbnail") or ""

    return MediaMetadata(
        title=info.get("title") or "Untitled media",
        uploader=(
            info.get("uploader")
            or info.get("channel")
            or first_entry.get("uploader")
            or first_entry.get("channel")
            or "Unknown uploader"
        ),
        duration=format_duration(info.get("duration")),
        thumbnail_url=thumbnail_url,
        thumbnail_data=_fetch_thumbnail(thumbnail_url, logger),
        selected_format=selected_format,
        webpage_url=info.get("webpage_url") or url,
        is_playlist=is_playlist,
        entry_count=entry_count,
    )


def _describe_selected_format(info: dict[str, Any], media_format: str, quality: str) -> str:
    prefix = "Playlist" if info.get("_type") == "playlist" else ""

    if media_format == "mp3":
        return f"{prefix} MP3 audio ({quality})".strip()

    height = info.get("height")
    ext = info.get("ext")

    if height and ext:
        return f"{prefix} {ext.upper()} video, up to {height}p ({quality})".strip()

    return f"{prefix} MP4 video ({quality})".strip()


def _entry_count(info: dict[str, Any]) -> int:
    entries = info.get("entries") or []

    if isinstance(entries, list):
        return len([entry for entry in entries if entry])

    playlist_count = info.get("playlist_count")
    if isinstance(playlist_count, int):
        return playlist_count

    return 0


def _first_entry(info: dict[str, Any]) -> dict[str, Any]:
    entries = info.get("entries") or []

    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict):
                return entry

    return {}


def _fetch_thumbnail(thumbnail_url: str, logger=None) -> bytes:
    if not thumbnail_url:
        return b""

    try:
        request = Request(
            thumbnail_url,
            headers={"User-Agent": "Audly/1.0"},
        )
        with urlopen(request, timeout=8) as response:
            return response.read()
    except Exception as exc:
        if logger:
            logger.warning(f"Could not load thumbnail preview: {exc}")
        return b""
