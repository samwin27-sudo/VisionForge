from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
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
from visionforge.ai.yolo_autolabeler import YoloSettings


class AutoLabelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YOLO Auto Label")
        self.setMinimumSize(680, 430)
        self.resize(720, 500)
        self.setSizeGripEnabled(True)

        title = QLabel("YOLO Auto Label")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        help_text = QLabel("Select a YOLO .pt model and detection settings. Predictions are added as reviewable annotations.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #9CA3AF;")

        self.model_path = QLineEdit()
        self.model_path.setPlaceholderText("Select YOLO .pt model file...")
        self.model_path.setMinimumWidth(360)
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        model_row = QHBoxLayout()
        model_row.setContentsMargins(0, 0, 0, 0)
        model_row.addWidget(self.model_path, 1)
        model_row.addWidget(browse)

        self.conf = QDoubleSpinBox()
        self.conf.setRange(0.01, 1.0)
        self.conf.setSingleStep(0.05)
        self.conf.setValue(0.25)

        self.iou = QDoubleSpinBox()
        self.iou.setRange(0.01, 1.0)
        self.iou.setSingleStep(0.05)
        self.iou.setValue(0.45)

        self.imgsz = QSpinBox()
        self.imgsz.setRange(128, 2048)
        self.imgsz.setSingleStep(32)
        self.imgsz.setValue(640)

        self.device = QComboBox()
        self.device.addItems(["auto", "cpu", "cuda"])

        self.auto_accept = QCheckBox("Auto-accept predictions above threshold")
        self.auto_thr = QDoubleSpinBox()
        self.auto_thr.setRange(0.01, 1.0)
        self.auto_thr.setSingleStep(0.05)
        self.auto_thr.setValue(0.80)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)
        form.addRow("Model path", model_row)
        form.addRow("Confidence", self.conf)
        form.addRow("IoU", self.iou)
        form.addRow("Image size", self.imgsz)
        form.addRow("Device", self.device)
        form.addRow(self.auto_accept, self.auto_thr)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 18, 18, 18)
        body_layout.setSpacing(12)
        body_layout.addWidget(title)
        body_layout.addWidget(help_text)
        body_layout.addLayout(form)
        body_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(body)

        run_btn = QPushButton("Run")
        cancel_btn = QPushButton("Cancel")
        run_btn.setMinimumWidth(100)
        cancel_btn.setMinimumWidth(100)
        run_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(run_btn)
        button_row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(scroll, 1)
        layout.addLayout(button_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select YOLO model", "", "YOLO model (*.pt);;All files (*)")
        if path:
            self.model_path.setText(path)

    def settings(self):
        return YoloSettings(
            self.model_path.text().strip(),
            float(self.conf.value()),
            float(self.iou.value()),
            int(self.imgsz.value()),
            self.device.currentText(),
            float(self.auto_thr.value()) if self.auto_accept.isChecked() else None,
        )
