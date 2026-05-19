import json
from PySide6.QtWidgets import QDialog,QHBoxLayout,QLabel,QPushButton,QTextEdit,QVBoxLayout
class ClassGroupDialog(QDialog):
    def __init__(self,classes,groups,parent=None):
        super().__init__(parent); self.setWindowTitle('ADAS Class Grouping Manager'); self.editor=QTextEdit(); sample=groups or {'Vehicle':['car','bus','truck'],'Bike':['motorcycle','bicycle'],'Pedestrian':['person','pedestrian'],'Road Damage':['pothole'],'Road Feature':['speedbreaker'],'Road Signage':['traffic_light','traffic_sign']}; self.editor.setPlainText(json.dumps(sample,indent=2)); ok=QPushButton('Save Groups'); cancel=QPushButton('Cancel'); ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject); row=QHBoxLayout(); row.addWidget(ok); row.addWidget(cancel); lay=QVBoxLayout(self); lay.addWidget(QLabel('Edit class_groups.json style mapping:')); lay.addWidget(self.editor); lay.addLayout(row)
    def groups(self): return json.loads(self.editor.toPlainText() or '{}')
