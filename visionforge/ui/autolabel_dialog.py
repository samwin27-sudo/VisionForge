from __future__ import annotations

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
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from visionforge.ai.class_mapper import DEFAULT_MAPPING_TEXT, parse_mapping_text
from visionforge.ai.yolo_autolabeler import YoloSettings
from visionforge.core.settings_manager import load_user_settings, save_user_settings


class AutoLabelDialog(QDialog):
    def __init__(self, parent=None, default_scope: str = "current"):
        super().__init__(parent)
        self.setWindowTitle("VisionForge Auto Annotate")
        self.setMinimumSize(760, 640)
        self.resize(820, 700)
        self._user_settings = load_user_settings()

        self.tabs = QTabWidget()
        self._build_run_tab(default_scope)
        self._build_mapping_tab()
        self._build_segmentation_tab()
        self._build_defaults_tab()

        run_btn = QPushButton("Run Auto Annotation")
        cancel_btn = QPushButton("Cancel")
        run_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        intro = QLabel("Auto-annotate a single image or the full dataset using YOLO, with optional SAM segmentation from detected boxes.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.tabs)
        layout.addLayout(btn_row)

    def _model_row(self, line_edit: QLineEdit, button_text: str, slot):
        browse = QPushButton(button_text)
        browse.clicked.connect(slot)
        row = QHBoxLayout()
        row.addWidget(line_edit, 1)
        row.addWidget(browse)
        return row

    def _build_run_tab(self, default_scope: str):
        tab = QWidget()
        form = QFormLayout(tab)

        self.scope = QComboBox()
        self.scope.addItem("Current image only", "current")
        self.scope.addItem("Full dataset", "dataset")
        self.scope.setCurrentIndex(1 if default_scope == "dataset" else 0)

        self.model_path = QLineEdit(self._user_settings.get("default_yolo_model", ""))
        self.conf = QDoubleSpinBox(); self.conf.setRange(0.01, 1.0); self.conf.setSingleStep(0.05); self.conf.setValue(0.25)
        self.iou = QDoubleSpinBox(); self.iou.setRange(0.01, 1.0); self.iou.setSingleStep(0.05); self.iou.setValue(0.45)
        self.imgsz = QSpinBox(); self.imgsz.setRange(128, 4096); self.imgsz.setSingleStep(32); self.imgsz.setValue(640)
        self.device = QComboBox(); self.device.addItems(["auto", "cpu", "cuda"]); self.device.setCurrentText(self._user_settings.get("default_device", "auto"))
        self.auto_accept = QCheckBox("Auto-accept predictions above threshold")
        self.auto_thr = QDoubleSpinBox(); self.auto_thr.setRange(0.01, 1.0); self.auto_thr.setSingleStep(0.05); self.auto_thr.setValue(0.80)

        self.use_segmentation = QCheckBox("After YOLO detection, use segmentation model on detected boxes")
        self.use_segmentation.setToolTip("This runs SAM on each detected box and stores a polygon with the bbox.")

        form.addRow("Auto annotation scope", self.scope)
        form.addRow("YOLO model", self._model_row(self.model_path, "Browse", self._browse_yolo))
        form.addRow("Confidence threshold", self.conf)
        form.addRow("IoU threshold", self.iou)
        form.addRow("Image size", self.imgsz)
        form.addRow("Device", self.device)
        form.addRow(self.auto_accept, self.auto_thr)
        form.addRow(self.use_segmentation)

        self.tabs.addTab(tab, "Run")

    def _build_mapping_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel(
            "Map model classes to project classes. Example: Vehicle = car, truck, bus, train. "
            "This mapping is applied to both single-image and full-dataset auto annotation."
        )
        label.setWordWrap(True)
        self.mapping_text = QTextEdit()
        self.mapping_text.setPlainText(self._user_settings.get("last_autolabel_mapping") or DEFAULT_MAPPING_TEXT)
        reset = QPushButton("Reset to ADAS/COCO example mapping")
        reset.clicked.connect(lambda: self.mapping_text.setPlainText(DEFAULT_MAPPING_TEXT))
        layout.addWidget(label)
        layout.addWidget(self.mapping_text, 1)
        layout.addWidget(reset)
        self.tabs.addTab(tab, "Class Mapping")

    def _build_segmentation_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.sam_path = QLineEdit(self._user_settings.get("default_segmentation_model", ""))
        self.sam_type = QComboBox(); self.sam_type.addItems(["auto", "vit_b", "vit_l", "vit_h"]); self.sam_type.setCurrentText(self._user_settings.get("default_sam_model_type", "auto"))
        self.sam_device = QComboBox(); self.sam_device.addItems(["auto", "cpu", "cuda"]); self.sam_device.setCurrentText(self._user_settings.get("default_device", "auto"))
        self.continue_if_sam_fails = QCheckBox("Continue YOLO auto-labeling if SAM fails")
        self.continue_if_sam_fails.setChecked(True)
        self.polygon_from_mask = QCheckBox("Convert SAM mask to polygon")
        self.polygon_from_mask.setChecked(True)

        form.addRow("SAM checkpoint", self._model_row(self.sam_path, "Browse", self._browse_sam))
        form.addRow("SAM model type", self.sam_type)
        form.addRow("SAM device", self.sam_device)
        form.addRow(self.polygon_from_mask)
        form.addRow(self.continue_if_sam_fails)
        self.tabs.addTab(tab, "Segmentation")

    def _build_defaults_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.save_yolo_default = QCheckBox("Set selected YOLO model as default")
        self.save_sam_default = QCheckBox("Set selected SAM model as default")
        self.save_mapping_default = QCheckBox("Remember this class mapping")
        self.save_mapping_default.setChecked(True)
        info = QLabel("Defaults are stored in ~/.visionforge/settings.json and reused until you change them.")
        info.setWordWrap(True)
        form.addRow(info)
        form.addRow(self.save_yolo_default)
        form.addRow(self.save_sam_default)
        form.addRow(self.save_mapping_default)
        self.tabs.addTab(tab, "Defaults")

    def _browse_yolo(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select YOLO model", "", "YOLO model (*.pt);;All files (*)")
        if p:
            self.model_path.setText(p)

    def _browse_sam(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select SAM checkpoint", "", "SAM checkpoint (*.pth);;All files (*)")
        if p:
            self.sam_path.setText(p)

    def selected_scope(self) -> str:
        return self.scope.currentData()

    def settings(self) -> YoloSettings:
        return YoloSettings(
            self.model_path.text().strip(),
            float(self.conf.value()),
            float(self.iou.value()),
            int(self.imgsz.value()),
            self.device.currentText(),
            float(self.auto_thr.value()) if self.auto_accept.isChecked() else None,
        )

    def class_mapping(self):
        return parse_mapping_text(self.mapping_text.toPlainText())

    def segmentation_options(self):
        return {
            "enabled": self.use_segmentation.isChecked(),
            "checkpoint_path": self.sam_path.text().strip(),
            "model_type": self.sam_type.currentText(),
            "device": self.sam_device.currentText(),
            "polygon_from_mask": self.polygon_from_mask.isChecked(),
            "continue_if_fails": self.continue_if_sam_fails.isChecked(),
        }

    def remember_defaults(self):
        data = {"default_device": self.device.currentText()}
        if self.save_yolo_default.isChecked():
            data["default_yolo_model"] = self.model_path.text().strip()
        if self.save_sam_default.isChecked():
            data["default_segmentation_model"] = self.sam_path.text().strip()
            data["default_sam_model_type"] = self.sam_type.currentText()
        if self.save_mapping_default.isChecked():
            data["last_autolabel_mapping"] = self.mapping_text.toPlainText()
        save_user_settings(data)
        return data
