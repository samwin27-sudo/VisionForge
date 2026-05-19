from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QInputDialog
class ClassPanel(QWidget):
    classAdded=Signal(str); classSelected=Signal(str); groupingRequested=Signal()
    def __init__(self,parent=None):
        super().__init__(parent); self.list_widget=QListWidget(); self.add_btn=QPushButton('Add Class'); self.group_btn=QPushButton('Class Groups'); lay=QVBoxLayout(self); lay.addWidget(QLabel('Classes')); lay.addWidget(self.list_widget); row=QHBoxLayout(); row.addWidget(self.add_btn); row.addWidget(self.group_btn); lay.addLayout(row); self.add_btn.clicked.connect(self._add); self.group_btn.clicked.connect(self.groupingRequested.emit); self.list_widget.currentTextChanged.connect(self.classSelected.emit)
    def set_classes(self,names): self.list_widget.clear(); self.list_widget.addItems(names); self.list_widget.setCurrentRow(0 if names else -1)
    def current_class(self): return self.list_widget.currentItem().text() if self.list_widget.currentItem() else 'object'
    def _add(self):
        name,ok=QInputDialog.getText(self,'Add Class','Class name:')
        if ok and name.strip(): self.classAdded.emit(name.strip())
