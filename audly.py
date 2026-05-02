import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ui.main_window import AudlyWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Helvetica Neue"))

    window = AudlyWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
