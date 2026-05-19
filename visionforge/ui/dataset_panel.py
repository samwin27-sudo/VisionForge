from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QListWidget, QVBoxLayout, QWidget
class DatasetPanel(QWidget):
    imageSelected=Signal(int)
    def __init__(self,parent=None):
        super().__init__(parent); self._items=[]; self.filter_edit=QLineEdit(); self.filter_edit.setPlaceholderText('Search/filter image names'); self.list_widget=QListWidget(); lay=QVBoxLayout(self); lay.addWidget(QLabel('Dataset Images')); lay.addWidget(self.filter_edit); lay.addWidget(self.list_widget); self.filter_edit.textChanged.connect(self._apply); self.list_widget.currentRowChanged.connect(self._row)
    def set_images(self,names): self._items=list(names); self._apply()
    def _apply(self):
        q=self.filter_edit.text().lower().strip(); self.list_widget.clear(); [self.list_widget.addItem(n) for n in self._items if not q or q in n.lower()]
    def _row(self,row):
        if row<0: return
        name=self.list_widget.item(row).text()
        if name in self._items: self.imageSelected.emit(self._items.index(name))
    def select_index(self,index):
        if 0<=index<self.list_widget.count(): self.list_widget.setCurrentRow(index)
