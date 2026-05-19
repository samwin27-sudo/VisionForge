from PySide6.QtWidgets import QCheckBox,QComboBox,QDialog,QDoubleSpinBox,QFileDialog,QFormLayout,QHBoxLayout,QLineEdit,QPushButton,QSpinBox,QVBoxLayout
from visionforge.ai.yolo_autolabeler import YoloSettings
class AutoLabelDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('YOLO Auto Label'); self.model_path=QLineEdit(); browse=QPushButton('Browse'); browse.clicked.connect(self._browse); mr=QHBoxLayout(); mr.addWidget(self.model_path); mr.addWidget(browse)
        self.conf=QDoubleSpinBox(); self.conf.setRange(.01,1); self.conf.setValue(.25); self.iou=QDoubleSpinBox(); self.iou.setRange(.01,1); self.iou.setValue(.45); self.imgsz=QSpinBox(); self.imgsz.setRange(128,2048); self.imgsz.setValue(640); self.device=QComboBox(); self.device.addItems(['auto','cpu','cuda']); self.auto_accept=QCheckBox('Auto-accept above threshold'); self.auto_thr=QDoubleSpinBox(); self.auto_thr.setRange(.01,1); self.auto_thr.setValue(.8)
        form=QFormLayout(); form.addRow('Model path',mr); form.addRow('Confidence',self.conf); form.addRow('IoU',self.iou); form.addRow('Image size',self.imgsz); form.addRow('Device',self.device); form.addRow(self.auto_accept,self.auto_thr); ok=QPushButton('Run'); cancel=QPushButton('Cancel'); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject); row=QHBoxLayout(); row.addWidget(ok); row.addWidget(cancel); lay=QVBoxLayout(self); lay.addLayout(form); lay.addLayout(row)
    def _browse(self):
        p,_=QFileDialog.getOpenFileName(self,'Select YOLO model','','YOLO model (*.pt);;All files (*)')
        if p: self.model_path.setText(p)
    def settings(self): return YoloSettings(self.model_path.text().strip(),float(self.conf.value()),float(self.iou.value()),int(self.imgsz.value()),self.device.currentText(),float(self.auto_thr.value()) if self.auto_accept.isChecked() else None)
