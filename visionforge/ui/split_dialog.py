from PySide6.QtWidgets import QDialog,QFileDialog,QFormLayout,QHBoxLayout,QLineEdit,QPushButton,QSpinBox,QVBoxLayout
class SplitDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Train / Val / Test Split'); self.train=QSpinBox(); self.train.setRange(1,98); self.train.setValue(70); self.val=QSpinBox(); self.val.setRange(1,98); self.val.setValue(20); self.test=QSpinBox(); self.test.setRange(1,98); self.test.setValue(10); self.output=QLineEdit(); b=QPushButton('Browse'); b.clicked.connect(self._browse); row=QHBoxLayout(); row.addWidget(self.output); row.addWidget(b); form=QFormLayout(); form.addRow('Train %',self.train); form.addRow('Val %',self.val); form.addRow('Test %',self.test); form.addRow('Output',row); ok=QPushButton('Split'); cancel=QPushButton('Cancel'); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject); btn=QHBoxLayout(); btn.addWidget(ok); btn.addWidget(cancel); lay=QVBoxLayout(self); lay.addLayout(form); lay.addLayout(btn)
    def _browse(self):
        p=QFileDialog.getExistingDirectory(self,'Select output folder')
        if p: self.output.setText(p)
    def options(self):
        t=self.train.value()+self.val.value()+self.test.value(); return {'output':self.output.text().strip(),'ratios':{'train':self.train.value()/t,'val':self.val.value()/t,'test':self.test.value()/t}}
