from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget


class ClassPanel(QWidget):
    classAdded = Signal(str)
    classSelected = Signal(str)
    classDeleted = Signal(str)
    groupingRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list = QListWidget()
        self.input = QLineEdit()
        self.input.setPlaceholderText("New class name")
        add = QPushButton("Add")
        delete = QPushButton("Delete Class")
        groups = QPushButton("Class Groups")

        add.clicked.connect(self._add)
        delete.clicked.connect(self._delete)
        groups.clicked.connect(self.groupingRequested.emit)
        self.list.currentTextChanged.connect(self.classSelected.emit)

        row = QHBoxLayout()
        row.addWidget(self.input, 1)
        row.addWidget(add)

        btns = QHBoxLayout()
        btns.addWidget(delete)
        btns.addWidget(groups)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Classes"))
        layout.addLayout(row)
        layout.addWidget(self.list)
        layout.addLayout(btns)

    def _add(self):
        name = self.input.text().strip()
        if name:
            self.classAdded.emit(name)
            self.input.clear()

    def _delete(self):
        item = self.list.currentItem()
        if item:
            self.classDeleted.emit(item.text())

    def set_classes(self, classes):
        current = self.list.currentItem().text() if self.list.currentItem() else None
        self.list.clear()
        self.list.addItems(list(classes))
        if current:
            matches = self.list.findItems(current, 0)
            if matches:
                self.list.setCurrentItem(matches[0])
