from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QInputDialog


class ClassPanel(QWidget):
    classAdded = Signal(str)
    classDeleted = Signal(str)
    classSelected = Signal(str)
    groupingRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_widget = QListWidget()
        self.add_btn = QPushButton('Add Class')
        self.delete_btn = QPushButton('Delete Class')
        self.group_btn = QPushButton('Class Groups')

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('Classes'))
        lay.addWidget(self.list_widget)

        row = QHBoxLayout()
        row.addWidget(self.add_btn)
        row.addWidget(self.delete_btn)
        lay.addLayout(row)
        lay.addWidget(self.group_btn)

        self.add_btn.clicked.connect(self._add)
        self.delete_btn.clicked.connect(self._delete)
        self.group_btn.clicked.connect(self.groupingRequested.emit)
        self.list_widget.currentTextChanged.connect(self.classSelected.emit)

    def set_classes(self, names):
        current = self.current_class()
        self.list_widget.clear()
        self.list_widget.addItems(names)
        if names:
            row = names.index(current) if current in names else 0
            self.list_widget.setCurrentRow(row)
        else:
            self.list_widget.setCurrentRow(-1)

    def current_class(self):
        return self.list_widget.currentItem().text() if self.list_widget.currentItem() else 'object'

    def _add(self):
        name, ok = QInputDialog.getText(self, 'Add Class', 'Class name:')
        if ok and name.strip():
            self.classAdded.emit(name.strip())

    def _delete(self):
        item = self.list_widget.currentItem()
        if item:
            self.classDeleted.emit(item.text())
