import json
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout


class ClassGroupDialog(QDialog):
    def __init__(self, classes, groups, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ADAS Class Grouping Manager")
        self.setMinimumSize(760, 560)
        self.resize(820, 620)
        self.setSizeGripEnabled(True)

        title = QLabel("ADAS Class Grouping Manager")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        help_text = QLabel("Edit a class_groups.json style mapping. Example: car + truck + bus -> Vehicle.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #9CA3AF;")

        self.editor = QTextEdit()
        self.editor.setMinimumHeight(360)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        sample = groups or {
            "Vehicle": ["car", "bus", "truck"],
            "Bike": ["motorcycle", "bicycle"],
            "Pedestrian": ["person", "pedestrian"],
            "Road Damage": ["pothole"],
            "Road Feature": ["speedbreaker"],
            "Road Signage": ["traffic_light", "traffic_sign"],
        }
        self.editor.setPlainText(json.dumps(sample, indent=2))

        save_btn = QPushButton("Save Groups")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        row = QHBoxLayout(); row.addStretch(1); row.addWidget(save_btn); row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(help_text)
        layout.addWidget(self.editor, 1)
        layout.addLayout(row)

    def groups(self):
        return json.loads(self.editor.toPlainText() or "{}")
