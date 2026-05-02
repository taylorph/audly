from services.metadata_service import MediaMetadata

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class PreviewPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(7)

        label = QLabel("Preview")
        label.setObjectName("fieldLabel")

        self.title = QLabel("Paste a URL and click Preview.")
        self.title.setObjectName("previewTitle")
        self.title.setWordWrap(True)

        self.meta = QLabel("Title, uploader, duration, and format will appear here.")
        self.meta.setObjectName("previewMeta")
        self.meta.setWordWrap(True)

        self.thumbnail = QLabel("Thumbnail preview")
        self.thumbnail.setObjectName("thumbnailPlaceholder")
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail.setMinimumHeight(130)

        layout.addWidget(label)
        layout.addWidget(self.title)
        layout.addWidget(self.meta)
        layout.addWidget(self.thumbnail)

    def show_loading(self):
        self.title.setText("Fetching video info...")
        self.meta.setText("Please wait while Audly checks the link.")
        self.thumbnail.clear()
        self.thumbnail.setText("Thumbnail preview")

    def show_metadata(self, metadata: MediaMetadata):
        self.title.setText(metadata.title)
        media_type = "Playlist" if metadata.is_playlist else "Video"
        count_line = f"\nItems: {metadata.entry_count}" if metadata.is_playlist and metadata.entry_count else ""
        self.meta.setText(
            f"Type: {media_type}{count_line}\n"
            f"Uploader: {metadata.uploader}\n"
            f"Duration: {metadata.duration}\n"
            f"Selected: {metadata.selected_format}"
        )

        self._show_thumbnail(metadata)

    def show_error(self, message: str):
        self.title.setText("Preview failed")
        self.meta.setText(message)
        self.thumbnail.clear()
        self.thumbnail.setText("Thumbnail preview")

    def _show_thumbnail(self, metadata: MediaMetadata):
        if not metadata.thumbnail_data:
            self.thumbnail.clear()
            self.thumbnail.setText("No thumbnail preview available")
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(metadata.thumbnail_data):
            self.thumbnail.clear()
            self.thumbnail.setText("Thumbnail preview failed")
            return

        scaled = pixmap.scaled(
            260,
            130,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.thumbnail.setPixmap(scaled)
