from PySide6.QtWidgets import QCheckBox,QDialog,QFileDialog,QFormLayout,QHBoxLayout,QLineEdit,QPushButton,QSpinBox,QVBoxLayout
class AugmentationDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Augment Dataset'); self.copies=QSpinBox(); self.copies.setRange(1,20); self.copies.setValue(1); self.hflip=QCheckBox('Horizontal flip'); self.hflip.setChecked(True); self.brightness=QCheckBox('Brightness adjustment'); self.brightness.setChecked(True); self.blur=QCheckBox('Blur'); self.output=QLineEdit(); b=QPushButton('Browse'); b.clicked.connect(self._browse); row=QHBoxLayout(); row.addWidget(self.output); row.addWidget(b); form=QFormLayout(); form.addRow('Copies per image',self.copies); form.addRow(self.hflip); form.addRow(self.brightness); form.addRow(self.blur); form.addRow('Output',row); ok=QPushButton('Augment'); cancel=QPushButton('Cancel'); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject); btn=QHBoxLayout(); btn.addWidget(ok); btn.addWidget(cancel); lay=QVBoxLayout(self); lay.addLayout(form); lay.addLayout(btn)
    def _browse(self):
        p=QFileDialog.getExistingDirectory(self,'Select output folder')
        if p: self.output.setText(p)
    def options(self): return {'output_dir':self.output.text().strip(),'copies_per_image':self.copies.value(),'horizontal_flip':self.hflip.isChecked(),'brightness':self.brightness.isChecked(),'blur':self.blur.isChecked()}
