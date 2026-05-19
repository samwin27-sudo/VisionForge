from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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


class SplitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Train / Val / Test Split")
        self.setMinimumSize(640, 380)
        self.resize(700, 430)
        self.setSizeGripEnabled(True)

        title = QLabel("Train / Val / Test Split")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        help_text = QLabel("Choose split ratios and an output folder. Ratios are normalized automatically.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #9CA3AF;")

        self.train = QSpinBox(); self.train.setRange(1, 98); self.train.setValue(70)
        self.val = QSpinBox(); self.val.setRange(1, 98); self.val.setValue(20)
        self.test = QSpinBox(); self.test.setRange(1, 98); self.test.setValue(10)

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
        form.addRow("Train %", self.train)
        form.addRow("Val %", self.val)
        form.addRow("Test %", self.test)
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

        split_btn = QPushButton("Split")
        cancel_btn = QPushButton("Cancel")
        split_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        row = QHBoxLayout(); row.addStretch(1); row.addWidget(split_btn); row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(scroll, 1)
        layout.addLayout(row)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select output folder", self.output.text().strip())
        if path:
            self.output.setText(path)

    def options(self):
        total = self.train.value() + self.val.value() + self.test.value()
        return {
            "output": self.output.text().strip(),
            "ratios": {
                "train": self.train.value() / total,
                "val": self.val.value() / total,
                "test": self.test.value() / total,
            },
        }
