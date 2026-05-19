from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(560, 240)
        self.resize(620, 280)
        self.setSizeGripEnabled(True)

        title = QLabel("VisionForge Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")

        text = QLabel(
            "VisionForge v1 stores project settings inside visionforge_project.json. "
            "AI model settings are selected when running auto-labeling. Export settings can be remembered per project."
        )
        text.setWordWrap(True)
        text.setStyleSheet("color: #CBD5E1;")

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch(1)
        layout.addWidget(close_btn)
