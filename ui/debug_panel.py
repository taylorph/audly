from datetime import datetime

from services.text_sanitizer import clean_message
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QVBoxLayout


class DebugPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(8)

        label = QLabel("Activity log")
        label.setObjectName("fieldLabel")

        self.log_output = QPlainTextEdit()
        self.log_output.setObjectName("debugLog")
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(120)

        layout.addWidget(label)
        layout.addWidget(self.log_output)

    def append(self, message: str):
        message = clean_message(message)
        if not message:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.appendPlainText(f"[{timestamp}] {message}")
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self):
        self.log_output.clear()
