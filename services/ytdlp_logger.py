from typing import Callable
from pathlib import Path

from services.text_sanitizer import clean_message


LogCallback = Callable[[str], None]


class YtdlpGuiLogger:
    def __init__(self, log_callback: LogCallback):
        self.log_callback = log_callback
        self._seen_messages = set()

    def debug(self, message: str):
        self._emit(message)

    def warning(self, message: str):
        self._emit(message)

    def error(self, message: str):
        self.log_callback(f"Error: {message}")

    def _emit(self, message: str):
        normalized = self._friendly_message(message)
        if not normalized or normalized in self._seen_messages:
            return

        self._seen_messages.add(normalized)
        self.log_callback(normalized)

    @staticmethod
    def _friendly_message(message: str) -> str:
        if not message:
            return ""

        text = clean_message(message)
        if not text or text.startswith("[debug] "):
            return ""

        if "No supported JavaScript runtime could be found" in text:
            return ""

        if "ffmpeg not found" in text.lower():
            return ""

        if "Downloading just the video" in text:
            return ""

        if "Deleting original file" in text:
            return ""

        if text.startswith("[youtube"):
            return ""

        if text.startswith("[info]"):
            return "Media stream selected."

        if text.startswith("[download] Destination:"):
            return "Preparing output file..."

        if text.startswith("[download] Download completed"):
            return "Media stream downloaded."

        if text.startswith("[ExtractAudio] Destination:"):
            return "Creating MP3 file..."

        if text.startswith("[Merger]"):
            return "Merging audio and video..."

        if text.endswith("started...") or text.endswith("finished"):
            return ""

        if "Destination:" in text:
            return f"Preparing output file: {Path(text.split('Destination:', 1)[1].strip()).name}"

        if text.startswith("Warning:"):
            return text

        return text
