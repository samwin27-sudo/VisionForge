from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ExportDialog(QDialog):
    DESCRIPTIONS = {
        "YOLO TXT": "Detection training format: images + one .txt label file per image.",
        "Pascal VOC XML": "Detection format with one XML file per image.",
        "COCO Detection JSON": "Single COCO JSON file with bbox annotations.",
        "COCO Segmentation JSON": "Single COCO JSON file with bbox + segmentation polygons/masks where available.",
        "CSV Summary": "Spreadsheet-friendly annotation summary for review and QA.",
        "Grouped YOLO": "YOLO export using your ADAS class groups instead of raw class names.",
    }

    def __init__(self, parent=None, initial_options=None):
        super().__init__(parent)
        self.setWindowTitle("Export Dataset")
        self.setMinimumSize(700, 440)
        self.resize(760, 500)
        self.setSizeGripEnabled(True)
        initial_options = initial_options or {}

        title = QLabel("Export Dataset")
        title.setObjectName("DialogTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")

        subtitle = QLabel("Choose the export format and output folder. Use Quick Export later to reuse these settings.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #9CA3AF;")

        self.format_box = QComboBox()
        self.format_box.setMinimumWidth(300)
        self.format_box.addItems(list(self.DESCRIPTIONS.keys()))
        initial_format = initial_options.get("format")
        if initial_format in self.DESCRIPTIONS:
            self.format_box.setCurrentText(initial_format)

        self.format_help = QLabel(self.DESCRIPTIONS[self.format_box.currentText()])
        self.format_help.setWordWrap(True)
        self.format_help.setMinimumHeight(42)
        self.format_help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.format_help.setStyleSheet("color: #CBD5E1;")
        self.format_box.currentTextChanged.connect(
            lambda text: self.format_help.setText(self.DESCRIPTIONS.get(text, ""))
        )

        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Choose output folder...")
        self.output_path.setText(initial_options.get("output", ""))
        self.output_path.setMinimumWidth(360)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse)

        output_row = QHBoxLayout()
        output_row.setContentsMargins(0, 0, 0, 0)
        output_row.addWidget(self.output_path, 1)
        output_row.addWidget(browse_btn)

        self.accepted_only = QCheckBox("Export accepted annotations only")
        self.accepted_only.setChecked(bool(initial_options.get("accepted_only", True)))

        self.remember_settings = QCheckBox("Remember these export settings for this project")
        self.remember_settings.setChecked(True)

        self.quick_export_hint = QLabel("Tip: after one export, use Quick Export or Ctrl+Shift+E to reuse these settings.")
        self.quick_export_hint.setWordWrap(True)
        self.quick_export_hint.setStyleSheet("color: #9CA3AF;")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)
        form.addRow("Export format", self.format_box)
        form.addRow("Format details", self.format_help)
        form.addRow("Output folder", output_row)
        form.addRow("", self.accepted_only)
        form.addRow("", self.remember_settings)
        form.addRow("", self.quick_export_hint)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 18, 18, 18)
        body_layout.setSpacing(12)
        body_layout.addWidget(title)
        body_layout.addWidget(subtitle)
        body_layout.addSpacing(4)
        body_layout.addLayout(form)
        body_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(body)

        export_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")
        export_btn.setMinimumWidth(110)
        cancel_btn.setMinimumWidth(100)
        export_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(export_btn)
        btn_row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(scroll, 1)
        layout.addLayout(btn_row)

    def _browse(self):
        start = self.output_path.text().strip() or ""
        path = QFileDialog.getExistingDirectory(self, "Select output folder", start)
        if path:
            self.output_path.setText(path)

    def options(self):
        return {
            "format": self.format_box.currentText(),
            "output": self.output_path.text().strip(),
            "accepted_only": self.accepted_only.isChecked(),
            "remember": self.remember_settings.isChecked(),
        }
