from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class AugmentationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Augment Dataset")
        self.setMinimumSize(660, 430)
        self.resize(720, 480)
        self.setSizeGripEnabled(True)

        title = QLabel("Augment Dataset")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        help_text = QLabel("Generate augmented copies while preserving bounding-box mappings where supported.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #9CA3AF;")

        self.copies = QSpinBox(); self.copies.setRange(1, 20); self.copies.setValue(1)
        self.hflip = QCheckBox("Horizontal flip"); self.hflip.setChecked(True)
        self.brightness = QCheckBox("Brightness adjustment"); self.brightness.setChecked(True)
        self.blur = QCheckBox("Blur")

        self.output = QLineEdit()
        self.output.setPlaceholderText("Choose output folder...")
        self.output.setMinimumWidth(360)
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        output_row = QHBoxLayout()
        output_row.setContentsMargins(0, 0, 0, 0)
        output_row.addWidget(self.output, 1)
        output_row.addWidget(browse)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)
        form.addRow("Copies per image", self.copies)
        form.addRow("", self.hflip)
        form.addRow("", self.brightness)
        form.addRow("", self.blur)
        form.addRow("Output folder", output_row)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 18, 18, 18)
        body_layout.setSpacing(12)
        body_layout.addWidget(title)
        body_layout.addWidget(help_text)
        body_layout.addLayout(form)
        body_layout.addStretch(1)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); scroll.setWidget(body)

        augment_btn = QPushButton("Augment")
        cancel_btn = QPushButton("Cancel")
        augment_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        row = QHBoxLayout(); row.addStretch(1); row.addWidget(augment_btn); row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(scroll, 1)
        layout.addLayout(row)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select output folder", self.output.text().strip())
        if path:
            self.output.setText(path)

    def options(self):
        return {
            "output_dir": self.output.text().strip(),
            "copies_per_image": self.copies.value(),
            "horizontal_flip": self.hflip.isChecked(),
            "brightness": self.brightness.isChecked(),
            "blur": self.blur.isChecked(),
        }
