from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel


class BrandLabel(QLabel):
    COLORS = [
        "#FF6B6B",
        "#FFD166",
        "#7BD88F",
        "#4D96FF",
        "#B983FF",
        "#FF8BD1",
    ]

    def __init__(self):
        super().__init__()
        self.setObjectName("brandLabel")
        self._index = 0

        self._timer = QTimer(self)
        self._timer.setInterval(360)
        self._timer.timeout.connect(self._advance)
        self._timer.start()
        self._render()

    def _advance(self):
        self._index = (self._index + 1) % len(self.COLORS)
        self._render()

    def _render(self):
        color = self.COLORS[self._index]
        self.setText(
            f'<span style="color:{color};">Fried</span>'
            '<span style="color:#F7F4EA;">Software</span>'
        )
