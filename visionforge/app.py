import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from visionforge.config import APP_NAME, VERSION
from visionforge.theme import dark_theme_qss
from visionforge.ui.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setStyleSheet(dark_theme_qss())
    try:
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as exc:
        QMessageBox.critical(None, APP_NAME, f"VisionForge could not start.\n\n{exc}")
        return 1
