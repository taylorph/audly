import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from models import ClipRange, DownloadRequest, MediaMetadata
from services.settings_service import SettingsService
from ui.brand_label import BrandLabel
from ui.debug_panel import DebugPanel
from ui.preview_panel import PreviewPanel
from ui.progress_panel import ProgressPanel
from ui.result_panel import ResultPanel
from ui.styles import APP_STYLESHEET
from workers import DownloadWorker, PreviewWorker


class AudlyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = SettingsService()
        self.download_path = self.settings.output_folder()
        self.has_custom_output_folder = self.settings.has_saved_output_folder()
        self.selected_format = "mp3"
        self.selected_quality = "best"
        self.preview_worker = None
        self.download_worker = None
        self.current_metadata: MediaMetadata | None = None

        self.setWindowTitle("Audly")
        self.setWindowIcon(QIcon("matchaicon.png"))
        self.resize(860, 900)
        self.setMinimumSize(760, 760)

        self._build_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self.debug_panel.append("Audly is ready.")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 20)
        root.setSpacing(10)

        title = QLabel("Audly")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(BrandLabel())
        header.addStretch(1)

        subtitle = QLabel("Your favorite GUI to download audio and video from supported media links.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        sites = QLabel("Download from YouTube, SoundCloud, TikTok, Twitch, Reddit, and more.")
        sites.setObjectName("sites")
        sites.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(6)

        self._build_url_controls(card_layout)
        self._build_format_controls(card_layout)
        self._build_clip_controls(card_layout)
        self._build_output_controls(card_layout)
        self._build_action_controls(card_layout)

        scroll = QScrollArea()
        scroll.setObjectName("scrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        scroll.setWidget(content)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(10)

        self.preview_panel = PreviewPanel()
        self.result_panel = ResultPanel()
        self.debug_panel = DebugPanel()

        content_layout.addWidget(self.preview_panel)
        content_layout.addWidget(self.result_panel)
        content_layout.addWidget(self.debug_panel)

        root.addLayout(header)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(sites)
        root.addWidget(card)
        root.addWidget(scroll, 1)

    def _build_url_controls(self, layout: QVBoxLayout):
        url_label = QLabel("Media URL")
        url_label.setObjectName("fieldLabel")

        url_row = QHBoxLayout()
        url_row.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Paste your media URL here...")
        self.url_input.setMinimumHeight(42)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setObjectName("secondaryButton")
        self.preview_btn.setMinimumHeight(42)
        self.preview_btn.setMinimumWidth(116)
        self.preview_btn.clicked.connect(self.preview)

        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.preview_btn)

        self.playlist_checkbox = QCheckBox("Include playlist")
        self.playlist_checkbox.setObjectName("playlistCheckbox")
        self.playlist_checkbox.setToolTip("Download the full playlist when the pasted URL contains one.")
        self.playlist_checkbox.stateChanged.connect(self.playlist_mode_changed)

        layout.addWidget(url_label)
        layout.addLayout(url_row)
        layout.addWidget(self.playlist_checkbox)
        layout.addSpacing(8)

    def _build_format_controls(self, layout: QVBoxLayout):
        format_quality_row = QHBoxLayout()
        format_quality_row.setSpacing(14)

        format_box = QVBoxLayout()
        format_box.setSpacing(6)
        format_label = QLabel("Format")
        format_label.setObjectName("fieldLabel")
        format_row = QHBoxLayout()
        format_row.setSpacing(10)

        self.format_group = QButtonGroup(self)
        self.format_group.setExclusive(True)
        self.mp3_btn = self._make_button("MP3", "mp3", self.set_format, self.format_group)
        self.mp4_btn = self._make_button("MP4", "mp4", self.set_format, self.format_group)
        self.mp3_btn.setChecked(True)

        format_row.addWidget(self.mp3_btn)
        format_row.addWidget(self.mp4_btn)
        format_box.addWidget(format_label)
        format_box.addLayout(format_row)

        quality_box = QVBoxLayout()
        quality_box.setSpacing(6)
        quality_label = QLabel("Quality")
        quality_label.setObjectName("fieldLabel")
        quality_row = QHBoxLayout()
        quality_row.setSpacing(10)

        self.quality_group = QButtonGroup(self)
        self.quality_group.setExclusive(True)
        self.best_quality_btn = self._make_button("Best", "best", self.set_quality, self.quality_group)
        self.standard_quality_btn = self._make_button("Standard", "standard", self.set_quality, self.quality_group)
        self.best_quality_btn.setChecked(True)

        quality_row.addWidget(self.best_quality_btn)
        quality_row.addWidget(self.standard_quality_btn)
        quality_box.addWidget(quality_label)
        quality_box.addLayout(quality_row)

        format_quality_row.addLayout(format_box)
        format_quality_row.addLayout(quality_box)
        layout.addLayout(format_quality_row)
        layout.addSpacing(8)

    def _build_clip_controls(self, layout: QVBoxLayout):
        clip_label = QLabel("Clip section")
        clip_label.setObjectName("fieldLabel")

        clip_top_row = QHBoxLayout()
        clip_top_row.setSpacing(10)

        self.clip_checkbox = QCheckBox("Only download part")
        self.clip_checkbox.setObjectName("clipCheckbox")

        time_help = QLabel("HH:MM:SS   Example: 00:02:00 to 00:02:30")
        time_help.setObjectName("timeHelp")

        clip_top_row.addWidget(self.clip_checkbox)
        clip_top_row.addWidget(time_help, 1)

        clip_row = QHBoxLayout()
        clip_row.setSpacing(10)

        self.start_input = QLineEdit()
        self.start_input.setObjectName("timeInput")
        self.start_input.setPlaceholderText("Start 00:02:00")
        self.start_input.setMinimumHeight(44)

        self.end_input = QLineEdit()
        self.end_input.setObjectName("timeInput")
        self.end_input.setPlaceholderText("End 00:02:30")
        self.end_input.setMinimumHeight(44)

        clip_row.addWidget(self.start_input)
        clip_row.addWidget(self.end_input)

        layout.addWidget(clip_label)
        layout.addLayout(clip_top_row)
        layout.addLayout(clip_row)
        layout.addSpacing(8)

    def _build_output_controls(self, layout: QVBoxLayout):
        name_label = QLabel("Save as")
        name_label.setObjectName("fieldLabel")

        self.title_input = QLineEdit()
        self.title_input.setObjectName("titleInput")
        self.title_input.setPlaceholderText("Leave blank to use the video title...")
        self.title_input.setMinimumHeight(40)

        output_label = QLabel("Output folder")
        output_label.setObjectName("fieldLabel")

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder_display = QLabel()
        self.folder_display.setObjectName("folderDisplay")
        self.folder_display.setMinimumHeight(42)

        self.folder_btn = QPushButton("Browse")
        self.folder_btn.setObjectName("secondaryButton")
        self.folder_btn.setMinimumHeight(42)
        self.folder_btn.setMinimumWidth(105)
        self.folder_btn.clicked.connect(self.choose_folder)

        folder_row.addWidget(self.folder_display, 1)
        folder_row.addWidget(self.folder_btn)

        layout.addWidget(name_label)
        layout.addWidget(self.title_input)
        layout.addSpacing(8)
        layout.addWidget(output_label)
        layout.addLayout(folder_row)
        layout.addSpacing(10)
        self._refresh_folder_display()

    def _build_action_controls(self, layout: QVBoxLayout):
        self.progress_panel = ProgressPanel()
        layout.addWidget(self.progress_panel)
        layout.addSpacing(8)

        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.setMinimumHeight(50)
        self.download_btn.clicked.connect(self.download)
        layout.addWidget(self.download_btn)

    def _make_button(self, text, value, setter, group):
        button = QPushButton(text)
        button.setObjectName("pillButton")
        button.setCheckable(True)
        button.setMinimumHeight(42)
        button.clicked.connect(lambda: setter(value))
        group.addButton(button)
        return button

    def set_format(self, value):
        self.selected_format = value
        self.progress_panel.status.setText(f"Selected format: {value.upper()}")
        self.debug_panel.append(f"Selected format: {value.upper()}")

    def set_quality(self, value):
        self.selected_quality = value
        self.progress_panel.status.setText(f"Selected quality: {value}")
        self.debug_panel.append(f"Selected quality: {value}")

    def playlist_mode_changed(self):
        if self.playlist_checkbox.isChecked():
            self.progress_panel.status.setText("Playlist downloads enabled")
            self.debug_panel.append("Playlist mode enabled. Playlist URLs will download every item.")
        else:
            self.progress_panel.status.setText("Single-video mode enabled")
            self.debug_panel.append("Playlist mode disabled. Playlist URLs will download only the selected video.")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.download_path)
        if not folder:
            return

        self.download_path = folder
        self.has_custom_output_folder = True
        self.settings.save_output_folder(folder)
        self._refresh_folder_display()
        self.progress_panel.status.setText("Output folder selected")
        self.debug_panel.append("Output folder selected.")

    def preview(self):
        url = self.url_input.text().strip()
        if not url:
            self.progress_panel.status.setText("Paste a URL first")
            self.debug_panel.append("Preview blocked: no URL provided.")
            return

        allow_playlist = self.playlist_checkbox.isChecked()
        self._set_busy(True)
        self.preview_panel.show_loading()
        self.progress_panel.reset("Fetching video info...")
        self.debug_panel.append("Fetching video info...")
        self.debug_panel.append(f"Preview mode: {'playlist' if allow_playlist else 'single-video'}")

        self.preview_worker = PreviewWorker(
            url,
            self.selected_format,
            self.selected_quality,
            allow_playlist,
        )
        self.preview_worker.log.connect(self.debug_panel.append)
        self.preview_worker.loaded.connect(self.preview_loaded)
        self.preview_worker.failed.connect(self.preview_failed)
        self.preview_worker.start()

    def preview_loaded(self, metadata: MediaMetadata):
        self.current_metadata = metadata
        self.preview_panel.show_metadata(metadata)

        if not self.title_input.text().strip() and not metadata.is_playlist:
            self.title_input.setText(metadata.title)

        self.progress_panel.status.setText(f"Preview loaded: {metadata.title}")
        self.debug_panel.append(f"Preview loaded: {metadata.title}")

        if metadata.thumbnail_url:
            self.debug_panel.append(f"Thumbnail URL: {metadata.thumbnail_url}")

        self._set_busy(False)

    def preview_failed(self, message: str):
        self.current_metadata = None
        self.preview_panel.show_error(message)
        self.progress_panel.reset("Preview failed")
        self.debug_panel.append(f"Preview failed: {message}")
        self._set_busy(False)

    def download(self):
        request = self._download_request()
        if request is None:
            return

        self.progress_panel.reset("Starting download...")
        self.result_panel.show_pending()
        self.debug_panel.append("Starting download...")
        self.debug_panel.append(
            "Download mode: playlist" if request.allow_playlist else "Download mode: single video"
        )
        if request.output_title:
            label = "playlist folder" if request.allow_playlist else "file name"
            self.debug_panel.append(f"Custom {label}: {request.output_title}")

        self._set_busy(True)
        self.download_worker = DownloadWorker(request)
        self.download_worker.progress.connect(self.progress_panel.set_progress)
        self.download_worker.log.connect(self.debug_panel.append)
        self.download_worker.done.connect(self.download_done)
        self.download_worker.failed.connect(self.download_failed)
        self.download_worker.start()

    def _download_request(self) -> DownloadRequest | None:
        url = self.url_input.text().strip()
        if not url:
            self.progress_panel.status.setText("Paste a URL first")
            self.debug_panel.append("Download blocked: no URL provided.")
            return None

        clip = ClipRange(
            enabled=self.clip_checkbox.isChecked(),
            start_time=self.start_input.text().strip(),
            end_time=self.end_input.text().strip(),
        )
        allow_playlist = self.playlist_checkbox.isChecked()

        if not self._validate_clip(clip, allow_playlist):
            return None

        return DownloadRequest(
            url=url,
            output_folder=self.download_path,
            media_format=self.selected_format,
            quality=self.selected_quality,
            clip=clip,
            allow_playlist=allow_playlist,
            output_title=self.title_input.text().strip(),
        )

    def _validate_clip(self, clip: ClipRange, allow_playlist: bool) -> bool:
        if clip.enabled and allow_playlist:
            return self._block_download("Clip downloads work on a single video. Turn off playlist mode or clip mode.")

        if not clip.enabled:
            return True

        if not self._valid_time(clip.start_time) or not self._valid_time(clip.end_time):
            return self._block_download("Use HH:MM:SS. Example: 00:02:00 to 00:02:30")

        if self._time_to_seconds(clip.start_time) >= self._time_to_seconds(clip.end_time):
            return self._block_download("Start time must be before end time.")

        return True

    def _block_download(self, message: str) -> bool:
        self.progress_panel.status.setText(message)
        self.debug_panel.append(f"Download blocked: {message}")
        return False

    def download_done(self, final_path: str):
        self.progress_panel.set_progress(100, message="Download complete")
        self.result_panel.show_success(self.download_path, final_path)
        self.debug_panel.append("Download complete")
        self.debug_panel.append(f"Output folder: {self.download_path}")

        if final_path:
            self.debug_panel.append(f"Saved file: {final_path}")
            self.progress_panel.status.setText(f"Download complete: {final_path}")

        self._set_busy(False)

    def download_failed(self, message: str):
        self.progress_panel.reset("Download failed")
        self.result_panel.show_error(message)
        self.debug_panel.append(f"Download failed: {message}")
        self._set_busy(False)

    def _set_busy(self, busy: bool):
        enabled = not busy
        self.download_btn.setEnabled(enabled)
        self.preview_btn.setEnabled(enabled)
        self.folder_btn.setEnabled(enabled)

    def _refresh_folder_display(self):
        if self.has_custom_output_folder:
            self.folder_display.setText(self.download_path)
            self.folder_display.setToolTip(self.download_path)
            return

        self.folder_display.setText("No folder selected yet - Browse or use Downloads")
        self.folder_display.setToolTip(f"Default output folder: {self.download_path}")

    @staticmethod
    def _valid_time(value: str) -> bool:
        return re.fullmatch(r"\d{2}:\d{2}:\d{2}", value) is not None

    @staticmethod
    def _time_to_seconds(value: str) -> int:
        hours, minutes, seconds = map(int, value.split(":"))
        return hours * 3600 + minutes * 60 + seconds
