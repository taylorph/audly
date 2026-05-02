from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class ProgressPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMinimumHeight(18)
        self.progress_bar.setMaximumHeight(18)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.status = QLabel("Ready")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(30)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status)

    def reset(self, message: str = "Ready"):
        self.progress_bar.setValue(0)
        self.status.setText(message)

    def set_progress(self, percent: int, speed: str = "", eta: str = "", message: str = ""):
        percent = max(0, min(100, percent))
        self.progress_bar.setValue(percent)

        details = []
        if speed:
            details.append(speed)
        if eta:
            details.append(f"ETA {eta}")

        status = message or f"Downloading... {percent}%"
        if details:
            status = f"{status} | {' | '.join(details)}"

        self.status.setText(status)
