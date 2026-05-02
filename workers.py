from PySide6.QtCore import QThread, Signal

from models import DownloadRequest
from services.download_service import DownloadService
from services.metadata_service import fetch_metadata
from services.ytdlp_logger import YtdlpGuiLogger


class PreviewWorker(QThread):
    loaded = Signal(object)
    log = Signal(str)
    failed = Signal(str)

    def __init__(self, url: str, media_format: str, quality: str, allow_playlist: bool):
        super().__init__()
        self.url = url
        self.media_format = media_format
        self.quality = quality
        self.allow_playlist = allow_playlist

    def run(self):
        try:
            metadata = fetch_metadata(
                self.url,
                self.media_format,
                self.quality,
                allow_playlist=self.allow_playlist,
                logger=YtdlpGuiLogger(self.log.emit),
            )
            self.loaded.emit(metadata)
        except Exception as exc:
            self.failed.emit(str(exc))


class DownloadWorker(QThread):
    progress = Signal(int, str, str, str)
    log = Signal(str)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, request: DownloadRequest):
        super().__init__()
        self.request = request

    def run(self):
        try:
            service = DownloadService(
                log_callback=self.log.emit,
                progress_callback=self.progress.emit,
            )
            final_path = service.download(self.request)
            self.done.emit(final_path)
        except Exception as exc:
            self.failed.emit(str(exc))
