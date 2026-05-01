from dataclasses import dataclass


@dataclass(frozen=True)
class ClipRange:
    enabled: bool = False
    start_time: str = ""
    end_time: str = ""


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    output_folder: str
    media_format: str
    quality: str
    clip: ClipRange
    allow_playlist: bool = False
    output_title: str = ""


@dataclass(frozen=True)
class MediaMetadata:
    title: str
    uploader: str
    duration: str
    thumbnail_url: str
    thumbnail_data: bytes
    selected_format: str
    webpage_url: str
    is_playlist: bool
    entry_count: int
