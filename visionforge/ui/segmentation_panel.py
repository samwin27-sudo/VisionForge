from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox,QDoubleSpinBox,QGroupBox,QPushButton,QVBoxLayout,QWidget
class SegmentationPanel(QWidget):
    generateMaskRequested=Signal(); visibilityChanged=Signal(bool); opacityChanged=Signal(float)
    def __init__(self,parent=None):
        super().__init__(parent); box=QGroupBox('Segmentation'); self.enable=QCheckBox('Segmentation Mode'); self.show=QCheckBox('Show masks/polygons'); self.show.setChecked(True); self.opacity=QDoubleSpinBox(); self.opacity.setRange(.05,1); self.opacity.setValue(.35); self.generate=QPushButton('Generate Mask From Selected Box'); lay=QVBoxLayout(box); [lay.addWidget(w) for w in [self.enable,self.show,self.opacity,self.generate]]; outer=QVBoxLayout(self); outer.addWidget(box); self.generate.clicked.connect(self.generateMaskRequested.emit); self.show.toggled.connect(self.visibilityChanged.emit); self.opacity.valueChanged.connect(self.opacityChanged.emit)
