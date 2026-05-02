from pathlib import Path

from PySide6.QtCore import QSettings


class SettingsService:
    def __init__(self):
        self.settings = QSettings("FriedSoftware", "Audly")

    def output_folder(self) -> str:
        saved = self.settings.value("output_folder", "", str)
        if saved and Path(saved).exists():
            return saved

        return str(Path.home() / "Downloads")

    def has_saved_output_folder(self) -> bool:
        saved = self.settings.value("output_folder", "", str)
        return bool(saved and Path(saved).exists())

    def save_output_folder(self, folder: str):
        self.settings.setValue("output_folder", folder)
