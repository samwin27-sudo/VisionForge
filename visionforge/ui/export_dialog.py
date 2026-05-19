from PySide6.QtWidgets import QCheckBox,QComboBox,QDialog,QFileDialog,QFormLayout,QHBoxLayout,QLineEdit,QPushButton,QVBoxLayout
class ExportDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Export Dataset'); self.format_box=QComboBox(); self.format_box.addItems(['YOLO TXT','Pascal VOC XML','COCO Detection JSON','COCO Segmentation JSON','CSV Summary','Grouped YOLO']); self.output_path=QLineEdit(); b=QPushButton('Browse'); b.clicked.connect(self._browse); row=QHBoxLayout(); row.addWidget(self.output_path); row.addWidget(b); self.accepted_only=QCheckBox('Export accepted annotations only'); self.accepted_only.setChecked(True); form=QFormLayout(); form.addRow('Format',self.format_box); form.addRow('Output',row); form.addRow(self.accepted_only); ok=QPushButton('Export'); cancel=QPushButton('Cancel'); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject); btn=QHBoxLayout(); btn.addWidget(ok); btn.addWidget(cancel); lay=QVBoxLayout(self); lay.addLayout(form); lay.addLayout(btn)
    def _browse(self):
        p=QFileDialog.getExistingDirectory(self,'Select output folder')
        if p: self.output_path.setText(p)
    def options(self): return {'format':self.format_box.currentText(),'output':self.output_path.text().strip(),'accepted_only':self.accepted_only.isChecked()}
