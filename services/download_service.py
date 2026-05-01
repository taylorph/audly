from pathlib import Path
from typing import Callable

import yt_dlp

from models import DownloadRequest
from services.file_naming_service import output_template
from services.ffmpeg_service import resolve_ffmpeg_location
from services.ytdlp_options import YOUTUBE_EXTRACTOR_ARGS
from services.ytdlp_logger import LogCallback, YtdlpGuiLogger


ProgressCallback = Callable[[int, str, str, str], None]


class DownloadService:
    def __init__(
        self,
        log_callback: LogCallback,
        progress_callback: ProgressCallback,
    ):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.final_path = ""
        self._last_logged_percent = -1

    def download(self, request: DownloadRequest) -> str:
        output_dir = Path(request.output_folder).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        ffmpeg_location = resolve_ffmpeg_location()
        if ffmpeg_location:
            self.log_callback("FFmpeg ready.")
        elif self._requires_ffmpeg(request):
            raise RuntimeError(
                "FFmpeg is required for this download. Run "
                "`python -m pip install -r requirements.txt` so Audly can use its packaged FFmpeg fallback, "
                "or install FFmpeg and make sure ffmpeg.exe is on PATH."
            )
        else:
            self.log_callback("Warning: FFmpeg was not found. MP3 conversion, merging, and clips may fail.")

        output_title = request.output_title
        if not request.allow_playlist and not output_title.strip():
            output_title = self._fetch_title_for_filename(
                request.url,
                ffmpeg_location,
                request.allow_playlist,
            )

        options = self._build_options(
            output_dir=output_dir,
            media_format=request.media_format,
            quality=request.quality,
            clip_enabled=request.clip.enabled,
            start_time=request.clip.start_time,
            end_time=request.clip.end_time,
            allow_playlist=request.allow_playlist,
            output_title=output_title,
            ffmpeg_location=ffmpeg_location,
        )

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=True)

        final_path = self._find_final_path(info, output_dir)
        if final_path:
            self.final_path = final_path

        self.progress_callback(100, "", "", "Download complete")
        return self.final_path or str(output_dir)

    def _fetch_title_for_filename(self, url: str, ffmpeg_location: str, allow_playlist: bool) -> str:
        self.log_callback("Resolving media title for output file...")
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": not allow_playlist,
            "extractor_args": YOUTUBE_EXTRACTOR_ARGS,
            "logger": YtdlpGuiLogger(self.log_callback),
        }

        if ffmpeg_location:
            options["ffmpeg_location"] = ffmpeg_location

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
            return info.get("title") or ""
        except Exception as exc:
            self.log_callback(f"Warning: could not resolve title before download: {exc}")
            return ""

    def _build_options(
        self,
        output_dir: Path,
        media_format: str,
        quality: str,
        clip_enabled: bool,
        start_time: str,
        end_time: str,
        allow_playlist: bool,
        output_title: str,
        ffmpeg_location: str,
    ) -> dict:
        options = {
            "outtmpl": output_template(output_dir, media_format, allow_playlist, output_title),
            "logger": YtdlpGuiLogger(self.log_callback),
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "noprogress": True,
            "noplaylist": not allow_playlist,
            "extractor_args": YOUTUBE_EXTRACTOR_ARGS,
            "windowsfilenames": True,
            "overwrites": False,
        }

        if ffmpeg_location:
            options["ffmpeg_location"] = ffmpeg_location

        if media_format == "mp3":
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "0" if quality == "best" else "5",
                        }
                    ],
                }
            )
        else:
            options.update(
                {
                    "format": (
                        "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
                        if quality == "best"
                        else "b[height<=720][ext=mp4]/best[height<=720]/best"
                    ),
                    "merge_output_format": "mp4",
                }
            )

        if clip_enabled:
            options["download_ranges"] = yt_dlp.utils.download_range_func(
                None,
                [(self._time_to_seconds(start_time), self._time_to_seconds(end_time))],
            )
            options["force_keyframes_at_cuts"] = True

        return options

    @staticmethod
    def _requires_ffmpeg(request: DownloadRequest) -> bool:
        return request.media_format in {"mp3", "mp4"} or request.clip.enabled

    def _progress_hook(self, data: dict):
        status = data.get("status")

        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes") or 0
            percent = int(downloaded * 100 / total) if total else 0
            speed = self._format_speed(data.get("speed"))
            eta = self._format_eta(data.get("eta"))
            message = f"Downloading... {percent}%"

            self.progress_callback(percent, speed, eta, message)
            if percent == 100 or percent - self._last_logged_percent >= 5:
                self._last_logged_percent = percent
                self.log_callback(
                    f"{message}"
                    + (f" | speed {speed}" if speed else "")
                    + (f" | ETA {eta}" if eta else "")
                )

        elif status == "finished":
            filename = data.get("filename") or ""
            if filename:
                self.final_path = filename
                self.log_callback(f"Downloaded file: {filename}")
            self.progress_callback(100, "", "", "Processing media...")

    def _postprocessor_hook(self, data: dict):
        status = data.get("status")
        postprocessor = data.get("postprocessor") or "Postprocessor"

        if status == "started":
            self.log_callback(f"{postprocessor} started...")
            self.progress_callback(100, "", "", "Processing media...")
        elif status == "finished":
            info = data.get("info_dict") or {}
            filepath = info.get("filepath") or info.get("_filename")
            if filepath:
                self.final_path = filepath
            self.log_callback(f"{postprocessor} finished")

    def _find_final_path(self, info: dict, output_dir: Path) -> str:
        requested_downloads = info.get("requested_downloads") or []

        for item in requested_downloads:
            filepath = item.get("filepath") or item.get("_filename") or item.get("filename")
            if filepath:
                return filepath

        filepath = info.get("filepath") or info.get("_filename")
        if filepath:
            return filepath

        if self.final_path:
            path = Path(self.final_path)
            if path.suffix.lower() != ".part":
                return str(path)

        candidates = sorted(
            output_dir.glob("*"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() != ".part":
                return str(candidate)

        return ""

    @staticmethod
    def _format_speed(speed) -> str:
        if not speed:
            return ""

        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        value = float(speed)
        unit_index = 0

        while value >= 1024 and unit_index < len(units) - 1:
            value /= 1024
            unit_index += 1

        return f"{value:.1f} {units[unit_index]}"

    @staticmethod
    def _format_eta(eta) -> str:
        if eta is None:
            return ""

        minutes, seconds = divmod(int(eta), 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

        return f"{minutes}:{seconds:02d}"

    @staticmethod
    def _time_to_seconds(value: str) -> float:
        hours, minutes, seconds = map(int, value.split(":"))
        return float(hours * 3600 + minutes * 60 + seconds)
