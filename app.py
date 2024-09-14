import sys
from typing import Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow
)

from utils.system import File, Path

from ui.main import Main_Page


class App():
    def __init__(
        self,
        config_dir: str = "config",
        config_file: str = "app.yaml"

    ) -> None:
        self.config: dict[str, Any] = self._Read_config(
            config_dir, config_file)
        self.app, self.main_window = self._Set_main_ui()

    def _Read_config(self, directory: str, file_name: str):
        _dir = Path.Join(directory, Path.WORK_SPACE)
        return File.YAML.Read(file_name, _dir)

    def _Set_main_ui(self) -> tuple[QApplication, QMainWindow]:
        _app = QApplication()
        _main_page = Main_Page("image process", [150, 150, 1000, 500])

        return _app, _main_page

    def Run(self):
        self.main_window.show()
        return self.app.exec()


if __name__ == "__main__":
    _app = App()

    # to do: app config update
    sys.exit(_app.Run())
