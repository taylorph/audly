import sys
import subprocess
import re
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QFrame, QButtonGroup,
    QProgressBar, QCheckBox
)


class DownloadWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    done = Signal()
    failed = Signal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                print(line, end="")

                match = re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%", line)
                if match:
                    percent = int(float(match.group(1)))
                    self.progress.emit(percent)
                    self.status.emit(f"Downloading... {percent}%")
                elif "ExtractAudio" in line:
                    self.status.emit("Converting audio...")
                elif "Merger" in line:
                    self.status.emit("Merging video and audio...")
                elif "Destination:" in line:
                    self.status.emit("Preparing file...")

            process.wait()

            if process.returncode == 0:
                self.progress.emit(100)
                self.done.emit()
            else:
                self.failed.emit("Download failed. Check Terminal.")

        except Exception as e:
            self.failed.emit(str(e))


class Audly(QWidget):
    def __init__(self):
        super().__init__()

        self.download_path = str(Path.home() / "Downloads")
        self.selected_format = "mp3"
        self.selected_quality = "best"
        self.worker = None

        self.setWindowTitle("Audly")
        self.setWindowIcon(QIcon("matchaicon.png"))  
        self.setFixedSize(700, 760)

        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(8)

        title = QLabel("Audly")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Your favorite GUI to download audio and video from supported media links.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        sites = QLabel("Download from YouTube, SoundCloud, TikTok, Twitch, Reddit, and more.")
        sites.setObjectName("sites")
        sites.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(6)

        url_label = QLabel("Media URL")
        url_label.setObjectName("fieldLabel")

        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Paste your media URL here...")
        self.url_input.setMinimumHeight(46)

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

        self.mp3_btn = self.make_button("MP3", "mp3", self.set_format, self.format_group)
        self.mp4_btn = self.make_button("MP4", "mp4", self.set_format, self.format_group)
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

        self.best_quality_btn = self.make_button("Best", "best", self.set_quality, self.quality_group)
        self.standard_quality_btn = self.make_button("Standard", "standard", self.set_quality, self.quality_group)
        self.best_quality_btn.setChecked(True)

        quality_row.addWidget(self.best_quality_btn)
        quality_row.addWidget(self.standard_quality_btn)

        quality_box.addWidget(quality_label)
        quality_box.addLayout(quality_row)

        format_quality_row.addLayout(format_box)
        format_quality_row.addLayout(quality_box)

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

        output_label = QLabel("Output folder")
        output_label.setObjectName("fieldLabel")

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder_display = QLabel(self.download_path)
        self.folder_display.setObjectName("folderDisplay")
        self.folder_display.setMinimumHeight(46)

        self.folder_btn = QPushButton("Browse")
        self.folder_btn.setObjectName("secondaryButton")
        self.folder_btn.setMinimumHeight(46)
        self.folder_btn.setMinimumWidth(105)
        self.folder_btn.clicked.connect(self.choose_folder)

        folder_row.addWidget(self.folder_display, 1)
        folder_row.addWidget(self.folder_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMinimumHeight(18)
        self.progress_bar.setMaximumHeight(18)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.setMinimumHeight(56)
        self.download_btn.clicked.connect(self.download)

        self.status = QLabel("Ready")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setMinimumHeight(28)

        card_layout.addWidget(url_label)
        card_layout.addWidget(self.url_input)
        card_layout.addSpacing(8)

        card_layout.addLayout(format_quality_row)
        card_layout.addSpacing(8)

        card_layout.addWidget(clip_label)
        card_layout.addLayout(clip_top_row)
        card_layout.addLayout(clip_row)
        card_layout.addSpacing(8)

        card_layout.addWidget(output_label)
        card_layout.addLayout(folder_row)
        card_layout.addSpacing(10)

        card_layout.addWidget(self.progress_bar)
        card_layout.addSpacing(12)

        card_layout.addWidget(self.download_btn)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.status)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(sites)
        root.addSpacing(8)
        root.addWidget(card)

    def make_button(self, text, value, setter, group):
        button = QPushButton(text)
        button.setObjectName("pillButton")
        button.setCheckable(True)
        button.setMinimumHeight(42)
        button.clicked.connect(lambda: setter(value))
        group.addButton(button)
        return button

    def set_format(self, value):
        self.selected_format = value
        self.status.setText(f"Selected format: {value.upper()}")

    def set_quality(self, value):
        self.selected_quality = value
        self.status.setText(f"Selected quality: {value}")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.download_path)

        if folder:
            self.download_path = folder
            self.folder_display.setText(folder)
            self.status.setText("Output folder selected")

    def valid_time(self, value):
        return re.fullmatch(r"\d{2}:\d{2}:\d{2}", value) is not None

    def time_to_seconds(self, value):
        hours, minutes, seconds = map(int, value.split(":"))
        return hours * 3600 + minutes * 60 + seconds

    def download(self):
        url = self.url_input.text().strip()

        if not url:
            self.status.setText("Paste a URL first")
            return

        clip_enabled = self.clip_checkbox.isChecked()
        start_time = self.start_input.text().strip()
        end_time = self.end_input.text().strip()

        if clip_enabled:
            if not self.valid_time(start_time) or not self.valid_time(end_time):
                self.status.setText("Use HH:MM:SS. Example: 00:02:00 to 00:02:30")
                return

            if self.time_to_seconds(start_time) >= self.time_to_seconds(end_time):
                self.status.setText("Start time must be before end time.")
                return

        output = str(Path(self.download_path) / "%(title)s.%(ext)s")

        if self.selected_format == "mp3":
            audio_quality = "0" if self.selected_quality == "best" else "5"
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-x", "--audio-format", "mp3", "--audio-quality", audio_quality,
                "-o", output
            ]
        else:
            video_format = (
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best"
                if self.selected_quality == "best"
                else "b[height<=720][ext=mp4]/best[height<=720]/best"
            )
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-f", video_format,
                "--merge-output-format", "mp4",
                "-o", output
            ]

        if clip_enabled:
            cmd.extend([
                "--download-sections", f"*{start_time}-{end_time}",
                "--force-keyframes-at-cuts"
            ])

        cmd.append(url)

        self.progress_bar.setValue(0)
        self.status.setText("Starting download...")
        self.download_btn.setEnabled(False)

        self.worker = DownloadWorker(cmd)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.done.connect(self.download_done)
        self.worker.failed.connect(self.download_failed)
        self.worker.start()

    def download_done(self):
        self.status.setText("Done")
        self.download_btn.setEnabled(True)

    def download_failed(self, message):
        self.status.setText(message)
        self.progress_bar.setValue(0)
        self.download_btn.setEnabled(True)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #08110D;
                color: #F3F1E8;
                font-family: "Helvetica Neue";
            }

            QLabel {
                background: transparent;
            }

            QLabel#title {
                color: #F7F4EA;
                font-size: 46px;
                font-weight: 900;
            }

            QLabel#subtitle {
                color: #B7BFAF;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#sites {
                color: #7F8A78;
                font-size: 12px;
                font-weight: 600;
            }

            QFrame#card {
                background-color: #121B16;
                border: 1px solid #2A372F;
                border-radius: 28px;
            }

            QLabel#fieldLabel {
                color: #E8E4D5;
                font-size: 13px;
                font-weight: 900;
                padding-left: 4px;
                padding-bottom: 1px;
            }

            QLabel#timeHelp {
                color: #8F9A87;
                font-size: 11px;
                font-weight: 700;
            }

            QLineEdit#urlInput, QLineEdit#timeInput {
                background-color: #07100C;
                color: #F7F4EA;
                border: 1px solid #405044;
                border-radius: 22px;
                padding-left: 18px;
                padding-right: 18px;
                font-size: 14px;
                font-weight: 700;
                selection-background-color: #8AA66E;
            }

            QLineEdit#urlInput:focus, QLineEdit#timeInput:focus {
                border: 2px solid #9DBB7D;
            }

            QCheckBox#clipCheckbox {
                color: #D8D5C7;
                font-size: 12px;
                font-weight: 800;
                spacing: 7px;
            }

            QCheckBox#clipCheckbox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 5px;
                border: 1px solid #405044;
                background-color: #07100C;
            }

            QCheckBox#clipCheckbox::indicator:checked {
                background-color: #8AA66E;
                border: 1px solid #A8C98A;
            }

            QPushButton#pillButton {
                background-color: #07100C;
                color: #D8D5C7;
                border: 1px solid #405044;
                border-radius: 21px;
                font-size: 13px;
                font-weight: 900;
            }

            QPushButton#pillButton:hover {
                background-color: #1B2A20;
                color: #F7F4EA;
            }

            QPushButton#pillButton:checked {
                background-color: #8AA66E;
                border: 1px solid #A8C98A;
                color: #08110D;
            }

            QLabel#folderDisplay {
                background-color: #07100C;
                color: #F7F4EA;
                border: 1px solid #405044;
                border-radius: 22px;
                padding-left: 18px;
                padding-right: 18px;
                font-size: 13px;
                font-weight: 700;
            }

            QPushButton#secondaryButton {
                background-color: #233122;
                color: #F7F4EA;
                border: 1px solid #4C6047;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 900;
            }

            QPushButton#secondaryButton:hover {
                background-color: #2C3C2A;
            }

            QProgressBar#progressBar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2E3A32,
                    stop:0.5 #1B241F,
                    stop:1 #0A120E
                );
                border: 1px solid #5F6F63;
                border-radius: 10px;
                padding: 2px;
            }

            QProgressBar#progressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A8D5BA,
                    stop:0.2 #C1E1C1,
                    stop:0.4 #F3E9B5,
                    stop:0.6 #F7C8A7,
                    stop:0.8 #D6C1F0,
                    stop:1 #A8D5BA
                );
            }

            QPushButton#primaryButton {
                background-color: #D7E8BF;
                color: #08110D;
                border: none;
                border-radius: 28px;
                font-size: 19px;
                font-weight: 900;
            }

            QPushButton#primaryButton:hover {
                background-color: #E4F0D4;
            }

            QPushButton#primaryButton:disabled {
                background-color: #4D5948;
                color: #9EA693;
            }

            QLabel#status {
                color: #A9B2A0;
                font-size: 13px;
                font-weight: 800;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Helvetica Neue"))

    window = Audly()
    window.show()

    sys.exit(app.exec())
