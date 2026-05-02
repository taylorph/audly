from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from services.text_sanitizer import clean_message


class ResultPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("resultPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(6)

        self.heading = QLabel("")
        self.heading.setObjectName("resultHeading")
        self.heading.setWordWrap(True)

        self.details = QLabel("")
        self.details.setObjectName("resultDetails")
        self.details.setWordWrap(True)

        layout.addWidget(self.heading)
        layout.addWidget(self.details)
        self.hide()

    def show_pending(self):
        self.setProperty("state", "pending")
        self._refresh_style()
        self.heading.setText("Download running")
        self.details.setText("Audly is working. Progress and yt-dlp messages are shown below.")
        self.show()

    def show_success(self, output_folder: str, final_path: str):
        self.setProperty("state", "success")
        self._refresh_style()
        self.heading.setText("Download complete")
        self.details.setText(f"Output folder: {output_folder}\nSaved file: {final_path or output_folder}")
        self.show()

    def show_error(self, message: str):
        self.setProperty("state", "error")
        self._refresh_style()
        self.heading.setText("Download failed")
        self.details.setText(clean_message(message))
        self.show()

    def clear(self):
        self.hide()
        self.heading.clear()
        self.details.clear()

    def _refresh_style(self):
        self.style().unpolish(self)
        self.style().polish(self)
