from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QFileDialog, QLabel, QMainWindow, QMessageBox, QProgressDialog, QPushButton, QListWidget, QSplitter, QToolBar, QVBoxLayout, QWidget, QDialog
from visionforge.ai.ai_review import accept_all, reject_all, set_status
from visionforge.ai.yolo_autolabeler import MissingYoloDependency, YoloAutoLabeler
from visionforge.analysis.dataset_analyzer import analyze_project
from visionforge.analysis.report_generator import generate_report
from visionforge.augment.augmentor import augment_project
from visionforge.config import APP_NAME, PROJECT_FILE_NAME, VERSION
from visionforge.core.annotation_store import Annotation, AnnotationStore
from visionforge.core.dataset_loader import load_dataset
from visionforge.core.project_io import load_project, save_project
from visionforge.exporters.coco_exporter import export_coco
from visionforge.exporters.csv_exporter import export_csv_summary
from visionforge.exporters.grouped_exporter import export_grouped
from visionforge.exporters.voc_exporter import export_voc
from visionforge.exporters.yolo_exporter import export_yolo
from visionforge.split.dataset_splitter import split_project
from visionforge.ui.annotation_canvas import AnnotationCanvas
from visionforge.ui.autolabel_dialog import AutoLabelDialog
from visionforge.ui.augmentation_dialog import AugmentationDialog
from visionforge.ui.class_group_dialog import ClassGroupDialog
from visionforge.ui.class_panel import ClassPanel
from visionforge.ui.dataset_panel import DatasetPanel
from visionforge.ui.export_dialog import ExportDialog
from visionforge.ui.insights_panel import InsightsPanel
from visionforge.ui.segmentation_panel import SegmentationPanel
from visionforge.ui.settings_dialog import SettingsDialog
from visionforge.ui.split_dialog import SplitDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1400, 850)
        self.store = AnnotationStore()
        self.current_image_index = -1
        self.current_class_name = "object"
        self.selected_annotation_id = None
        self._build_ui()
        self._build_toolbar()
        self._shortcuts()
        self._status("Ready")

    def _build_ui(self):
        self.dataset_panel = DatasetPanel()
        self.class_panel = ClassPanel()
        self.class_panel.classAdded.connect(self.add_class)
        self.class_panel.classSelected.connect(lambda n: setattr(self, "current_class_name", n or "object"))
        self.class_panel.groupingRequested.connect(self.open_group_manager)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self.dataset_panel)
        left_layout.addWidget(self.class_panel)

        self.canvas = AnnotationCanvas()
        self.canvas.annotationCreated.connect(self.add_bbox_annotation)
        self.canvas.annotationSelected.connect(self._annotation_selected)
        self.dataset_panel.imageSelected.connect(self.load_image_index)

        self.annotation_list = QListWidget()
        self.accept_btn = QPushButton("Accept Selected")
        self.reject_btn = QPushButton("Reject Selected")
        self.accept_all_btn = QPushButton("Accept All Pending")
        self.reject_all_btn = QPushButton("Reject All Pending")
        self.accept_btn.clicked.connect(lambda: self._set_selected_status("accepted"))
        self.reject_btn.clicked.connect(lambda: self._set_selected_status("rejected"))
        self.accept_all_btn.clicked.connect(self._accept_all_current)
        self.reject_all_btn.clicked.connect(self._reject_all_current)
        self.segmentation_panel = SegmentationPanel()
        self.segmentation_panel.visibilityChanged.connect(self._toggle_masks)
        self.segmentation_panel.opacityChanged.connect(self._set_mask_opacity)
        self.segmentation_panel.generateMaskRequested.connect(self._segmentation_not_configured)
        self.insights = InsightsPanel()
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Current Image Annotations"))
        right_layout.addWidget(self.annotation_list)
        for widget in [self.accept_btn, self.reject_btn, self.accept_all_btn, self.reject_all_btn, self.segmentation_panel, self.insights]:
            right_layout.addWidget(widget)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 1)
        self.setCentralWidget(splitter)

    def _build_toolbar(self):
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        actions = [
            ("Open Dataset", self.open_dataset),
            ("Save Project", self.save_project),
            ("Auto Label", self.auto_label_current),
            ("Segmentation Mode", self._segmentation_not_configured),
            ("Analyze Dataset", self.analyze_dataset),
            ("Augment Dataset", self.augment_dataset),
            ("Split Dataset", self.split_dataset),
            ("Export", self.export_dataset),
            ("Generate Report", self.generate_report),
            ("Settings", self.open_settings),
        ]
        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

    def _shortcuts(self):
        pairs = [
            ("Ctrl+O", self.open_dataset),
            ("Ctrl+S", self.save_project),
            ("Ctrl+E", self.export_dataset),
            ("Ctrl+R", self.generate_report),
            ("Ctrl+A", self.auto_label_current),
            ("Ctrl+Shift+A", self.auto_label_full_dataset),
            ("Ctrl+M", lambda: self._toggle_masks(not self.canvas.show_masks)),
            ("Ctrl+G", self.open_group_manager),
            ("A", self.previous_image),
            ("D", self.next_image),
            ("Delete", self.delete_selected_annotation),
            ("Space", lambda: self._set_selected_status("accepted")),
            ("X", lambda: self._set_selected_status("rejected")),
        ]
        for key, callback in pairs:
            QShortcut(QKeySequence(key), self).activated.connect(callback)
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.previous_image)
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.next_image)

    def _status(self, message):
        idx = self.current_image_index + 1 if self.current_image_index >= 0 else 0
        self.statusBar().showMessage(f"{message} | Image {idx}/{len(self.store.images)} | Mode: detection | AI model: lazy-load")

    def open_dataset(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Dataset Folder")
        if not folder:
            return
        try:
            project_path = Path(folder) / PROJECT_FILE_NAME
            self.store = AnnotationStore(load_project(project_path)) if project_path.exists() else AnnotationStore()
            if not project_path.exists():
                self.store.set_dataset(folder, load_dataset(folder))
                self.store.add_class("object")
            self.dataset_panel.set_images([image.relative_path for image in self.store.images])
            self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
            self.load_image_index(0 if self.store.images else -1)
            self._status(f"Loaded {len(self.store.images)} images")
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Could not open dataset.\n\n{exc}")

    def save_project(self):
        if not self.store.project.dataset_path:
            return
        path = save_project(self.store.project)
        self._status(f"Saved {path.name}")

    def load_image_index(self, index):
        if index < 0 or index >= len(self.store.images):
            self.canvas.clear()
            self.current_image_index = -1
            return
        self.current_image_index = index
        image = self.store.images[index]
        self.canvas.load_image(Path(self.store.project.dataset_path) / image.relative_path, image)
        self._refresh_annotation_list()
        self._status(image.relative_path)

    def next_image(self):
        if self.current_image_index + 1 < len(self.store.images):
            self.dataset_panel.select_index(self.current_image_index + 1)

    def previous_image(self):
        if self.current_image_index > 0:
            self.dataset_panel.select_index(self.current_image_index - 1)

    def add_class(self, name):
        self.store.add_class(name)
        self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
        self.save_project()

    def add_bbox_annotation(self, bbox):
        if self.current_image_index < 0:
            return
        class_id = self.store.add_class(self.current_class_name)
        annotation = Annotation(bbox=bbox, class_name=self.current_class_name, class_id=class_id, source="manual", status="accepted")
        self.store.add_annotation(self.current_image_index, annotation)
        self.selected_annotation_id = annotation.annotation_id
        self.canvas.selected_annotation_id = annotation.annotation_id
        self.save_project()
        self._refresh_annotation_list()
        self.canvas.update()

    def _annotation_selected(self, annotation_id):
        self.selected_annotation_id = annotation_id
        self.canvas.selected_annotation_id = annotation_id
        self._refresh_annotation_list()

    def _refresh_annotation_list(self):
        self.annotation_list.clear()
        if self.current_image_index < 0:
            return
        for annotation in self.store.images[self.current_image_index].annotations:
            text = f"{annotation.class_name} | {annotation.status} | {annotation.source}"
            if annotation.confidence is not None:
                text += f" | {annotation.confidence:.2f}"
            self.annotation_list.addItem(text)

    def _selected_annotation(self):
        if self.current_image_index < 0 or not self.selected_annotation_id:
            return None
        return self.store.get_annotation(self.current_image_index, self.selected_annotation_id)

    def _set_selected_status(self, status):
        annotation = self._selected_annotation()
        if annotation:
            set_status(annotation, status)
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()

    def _accept_all_current(self):
        if self.current_image_index >= 0:
            count = accept_all(self.store.images[self.current_image_index])
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()
            self._status(f"Accepted {count} predictions")

    def _reject_all_current(self):
        if self.current_image_index >= 0:
            count = reject_all(self.store.images[self.current_image_index])
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()
            self._status(f"Rejected {count} predictions")

    def delete_selected_annotation(self):
        if self.current_image_index >= 0 and self.selected_annotation_id:
            self.store.delete_annotation(self.current_image_index, self.selected_annotation_id)
            self.selected_annotation_id = None
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()

    def auto_label_current(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, APP_NAME, "Open a dataset and select an image first.")
            return
        dialog = AutoLabelDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run_yolo_on_indices([self.current_image_index], dialog.settings())

    def auto_label_full_dataset(self):
        if not self.store.images:
            QMessageBox.information(self, APP_NAME, "Open a dataset first.")
            return
        dialog = AutoLabelDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._run_yolo_on_indices(list(range(len(self.store.images))), dialog.settings())

    def _run_yolo_on_indices(self, indices, settings):
        try:
            lookup = {c["name"]: int(c["id"]) for c in self.store.project.classes}
            labeler = YoloAutoLabeler(settings)
            progress = QProgressDialog("Running YOLO auto-labeling...", "Cancel", 0, len(indices), self)
            total = 0
            for step, index in enumerate(indices, 1):
                if progress.wasCanceled():
                    break
                image = self.store.images[index]
                annotations = labeler.predict_image(Path(self.store.project.dataset_path) / image.relative_path, lookup)
                for annotation in annotations:
                    if self.store.get_class_by_name(annotation.class_name) is None:
                        annotation.class_id = self.store.add_class(annotation.class_name)
                    self.store.add_annotation(index, annotation)
                total += len(annotations)
                progress.setValue(step)
            self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()
            self._status(f"YOLO added {total} predictions")
        except MissingYoloDependency as exc:
            QMessageBox.information(self, APP_NAME, str(exc))
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Auto-labeling failed.\n\n{exc}")

    def _segmentation_not_configured(self):
        QMessageBox.information(self, APP_NAME, "Segmentation assistant is optional. Install with pip install -r requirements-segmentation.txt. The SAM backend is in visionforge/ai/sam_segmenter.py and mask/polygon utilities are ready for integration.")

    def _toggle_masks(self, value):
        self.canvas.show_masks = value
        self.canvas.update()

    def _set_mask_opacity(self, value):
        self.canvas.mask_opacity = value
        self.canvas.update()

    def analyze_dataset(self):
        self.insights.set_summary(analyze_project(self.store.project))
        self._status("Dataset analysis complete")

    def export_dataset(self):
        dialog = ExportDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        options = dialog.options()
        if not options["output"]:
            return
        output = Path(options["output"])
        try:
            fmt = options["format"]
            if fmt == "YOLO TXT":
                export_yolo(self.store.project, output / "yolo", options["accepted_only"])
            elif fmt == "Pascal VOC XML":
                export_voc(self.store.project, output / "voc", options["accepted_only"])
            elif fmt == "COCO Detection JSON":
                export_coco(self.store.project, output / "coco_detection.json", False, options["accepted_only"])
            elif fmt == "COCO Segmentation JSON":
                export_coco(self.store.project, output / "coco_segmentation.json", True, options["accepted_only"])
            elif fmt == "CSV Summary":
                export_csv_summary(self.store.project, output / "annotation_summary.csv", options["accepted_only"])
            elif fmt == "Grouped YOLO":
                export_grouped(self.store.project, output, "yolo")
            QMessageBox.information(self, APP_NAME, f"Export complete:\n{output}")
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Export failed.\n\n{exc}")

    def generate_report(self):
        folder = QFileDialog.getExistingDirectory(self, "Select report output folder")
        if not folder:
            return
        try:
            generate_report(self.store.project, folder)
            QMessageBox.information(self, APP_NAME, f"Report generated:\n{folder}")
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Report generation failed.\n\n{exc}")

    def split_dataset(self):
        dialog = SplitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.options()
            config = split_project(self.store.project, options["output"], options["ratios"])
            self.store.project.split_info = config
            self.save_project()
            QMessageBox.information(self, APP_NAME, "Split complete.")

    def augment_dataset(self):
        dialog = AugmentationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            augment_project(self.store.project, **dialog.options())
            QMessageBox.information(self, APP_NAME, "Augmentation complete. Segmentation-safe augmentation is limited in v1.")

    def open_group_manager(self):
        dialog = ClassGroupDialog([c["name"] for c in self.store.project.classes], self.store.project.class_groups, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.store.project.class_groups = dialog.groups()
                self.save_project()
            except Exception as exc:
                QMessageBox.warning(self, APP_NAME, f"Invalid group JSON.\n\n{exc}")

    def open_settings(self):
        SettingsDialog(self).exec()
