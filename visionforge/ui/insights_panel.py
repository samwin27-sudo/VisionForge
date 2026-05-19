from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

class InsightsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dataset Insights"))
        layout.addWidget(self.text)
        self.set_summary({})
    def set_summary(self, summary):
        if not summary:
            self.text.setPlainText("Open a dataset and click Analyze Dataset to see insights.")
            return
        lines = [
            f"Images: {summary.get('total_images', 0)}",
            f"Annotated images: {summary.get('total_annotated_images', 0)}",
            f"Annotations: {summary.get('total_annotations', 0)}",
            f"Boxes: {summary.get('total_bounding_boxes', 0)}",
            f"Segmentation: {summary.get('total_segmentation_masks', 0)}",
            f"Class imbalance: {summary.get('class_imbalance_ratio', 0):.2f}",
            "",
            "Class counts:",
        ]
        lines += [f"- {k}: {v}" for k, v in summary.get("class_wise_object_count", {}).items()]
        self.text.setPlainText("\n".join(lines))
