from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout


class AugmentationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Augment Dataset")
        self.setMinimumSize(620, 560)
        self.resize(680, 620)

        self.copies = QSpinBox(); self.copies.setRange(1, 50); self.copies.setValue(1)
        self.hflip = QCheckBox("Horizontal flip")
        self.hflip.setChecked(True)
        self.vflip = QCheckBox("Vertical flip")
        self.brightness = QCheckBox("Brightness adjustment")
        self.brightness.setChecked(True)
        self.contrast = QCheckBox("Contrast adjustment")
        self.grayscale = QCheckBox("Grayscale")
        self.blur = QCheckBox("Gaussian blur")
        self.noise = QCheckBox("Noise")
        self.sharpen = QCheckBox("Sharpen")
        self.saturation = QCheckBox("Saturation / color jitter")
        self.rotate = QCheckBox("Small-angle rotation with bbox correction")
        self.random_crop = QCheckBox("Random crop with bbox correction")
        self.resize_enabled = QCheckBox("Resize long side")
        self.resize_to = QSpinBox(); self.resize_to.setRange(128, 4096); self.resize_to.setValue(640); self.resize_to.setSingleStep(32)
        self.output = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        out_row = QHBoxLayout(); out_row.addWidget(self.output, 1); out_row.addWidget(browse)

        form = QFormLayout()
        form.addRow("Copies per image", self.copies)
        for cb in [self.hflip, self.vflip, self.brightness, self.contrast, self.grayscale, self.blur, self.noise, self.sharpen, self.saturation, self.rotate, self.random_crop]:
            form.addRow(cb)
        form.addRow(self.resize_enabled, self.resize_to)
        form.addRow("Output folder", out_row)

        info = QLabel("Note: bbox correction is supported for these transforms. Segmentation-safe augmentation is limited; masks/polygons may be dropped for unsafe transforms.")
        info.setWordWrap(True)

        ok = QPushButton("Augment")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btn = QHBoxLayout(); btn.addStretch(1); btn.addWidget(ok); btn.addWidget(cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addLayout(btn)

    def _browse(self):
        p = QFileDialog.getExistingDirectory(self, "Select output folder")
        if p:
            self.output.setText(p)

    def options(self):
        return {
            "output_dir": self.output.text().strip(),
            "copies_per_image": self.copies.value(),
            "horizontal_flip": self.hflip.isChecked(),
            "vertical_flip": self.vflip.isChecked(),
            "brightness": self.brightness.isChecked(),
            "contrast": self.contrast.isChecked(),
            "grayscale": self.grayscale.isChecked(),
            "blur": self.blur.isChecked(),
            "noise": self.noise.isChecked(),
            "sharpen": self.sharpen.isChecked(),
            "saturation": self.saturation.isChecked(),
            "rotate": self.rotate.isChecked(),
            "random_crop": self.random_crop.isChecked(),
            "resize_to": self.resize_to.value() if self.resize_enabled.isChecked() else None,
        }
