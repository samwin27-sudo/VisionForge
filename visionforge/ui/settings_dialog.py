from PySide6.QtWidgets import QDialog,QLabel,QPushButton,QVBoxLayout
class SettingsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Settings'); lay=QVBoxLayout(self); lay.addWidget(QLabel('VisionForge v1 settings are stored in visionforge_project.json. AI settings are selected per run.')); close=QPushButton('Close'); close.clicked.connect(self.accept); lay.addWidget(close)
