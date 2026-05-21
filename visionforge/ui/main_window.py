from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QDialog,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QListWidget,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from visionforge.ai.ai_review import accept_all, reject_all, set_status
from visionforge.ai.sam_segmenter import SamSegmenter, SamSettings
from visionforge.ai.segmentation_backend import MissingSegmentationDependency
from visionforge.ai.yolo_autolabeler import MissingYoloDependency, YoloAutoLabeler
from visionforge.analysis.dataset_analyzer import analyze_project
from visionforge.analysis.report_generator import generate_report
from visionforge.augment.augmentor import augment_project
from visionforge.config import APP_NAME, PROJECT_FILE_NAME, VERSION
from visionforge.core.annotation_store import Annotation, AnnotationStore
from visionforge.core.dataset_loader import load_dataset
from visionforge.core.mask_utils import mask_to_polygons
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
        self.resize(1450, 880)
        self.store = AnnotationStore()
        self.current_image_index = -1
        self.current_class_name = "object"
        self.selected_annotation_id = None
        self._sam_warning_shown = False
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
        if hasattr(self.class_panel, "classDeleted"):
            self.class_panel.classDeleted.connect(self.delete_class)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self.dataset_panel)
        left_layout.addWidget(self.class_panel)

        self.canvas = AnnotationCanvas()
        self.canvas.annotationCreated.connect(self.add_bbox_annotation)
        self.canvas.annotationSelected.connect(self._annotation_selected)
        if hasattr(self.canvas, "annotationChanged"):
            self.canvas.annotationChanged.connect(self._annotation_changed)
        if hasattr(self.canvas, "deleteRequested"):
            self.canvas.deleteRequested.connect(self.delete_selected_annotation)
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
        self.segmentation_panel.generateMaskRequested.connect(self.generate_mask_for_selected_bbox)

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
            ("Auto Annotate", self.auto_annotate),
            ("Auto Annotate Full Dataset", self.auto_label_full_dataset),
            ("Analyze Dataset", self.analyze_dataset),
            ("Augment Dataset", self.augment_dataset),
            ("Split Dataset", self.split_dataset),
            ("Export", self.export_dataset),
            ("Quick Export", self.quick_export),
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
            ("Ctrl+Shift+E", self.quick_export),
            ("Ctrl+R", self.generate_report),
            ("Ctrl+A", self.auto_label_current),
            ("Ctrl+Shift+A", self.auto_label_full_dataset),
            ("Ctrl+M", lambda: self._toggle_masks(not self.canvas.show_masks)),
            ("Ctrl+G", self.open_group_manager),
            ("A", self.previous_image),
            ("D", self.next_image),
            ("Delete", self.delete_selected_annotation),
            ("Backspace", self.delete_selected_annotation),
            ("Space", lambda: self._set_selected_status("accepted")),
            ("X", lambda: self._set_selected_status("rejected")),
        ]
        for key, callback in pairs:
            QShortcut(QKeySequence(key), self).activated.connect(callback)
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.previous_image)
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.next_image)

    def _status(self, message):
        idx = self.current_image_index + 1 if self.current_image_index >= 0 else 0
        self.statusBar().showMessage(f"{message} | Image {idx}/{len(self.store.images)} | Mode: detection/segmentation | AI: optional")

    def _refresh_class_colors(self):
        if hasattr(self.canvas, "set_class_colors"):
            self.canvas.set_class_colors(self.store.class_color_lookup())

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
            self._refresh_class_colors()
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
        self._refresh_class_colors()
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
        self._refresh_class_colors()
        self.save_project()

    def delete_class(self, name):
        if not name:
            return
        ok = QMessageBox.question(
            self,
            APP_NAME,
            f"Delete class '{name}'?\n\nAnnotations using this class will also be removed.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ok != QMessageBox.Yes:
            return
        self.store.delete_class(name, remove_annotations=True)
        self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
        self._refresh_class_colors()
        self.save_project()
        self._refresh_annotation_list()
        self.canvas.update()

    def add_bbox_annotation(self, bbox):
        if self.current_image_index < 0:
            return
        class_id = self.store.add_class(self.current_class_name)
        annotation = Annotation(bbox=bbox, class_name=self.current_class_name, class_id=class_id, source="manual", status="accepted")
        self.store.add_annotation(self.current_image_index, annotation)
        self.selected_annotation_id = annotation.annotation_id
        self.canvas.selected_annotation_id = annotation.annotation_id
        self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
        self._refresh_class_colors()
        self.save_project()
        self._refresh_annotation_list()
        self.canvas.update()

    def _annotation_selected(self, annotation_id):
        self.selected_annotation_id = annotation_id
        self.canvas.selected_annotation_id = annotation_id
        self._refresh_annotation_list()

    def _annotation_changed(self, annotation_id):
        self.selected_annotation_id = annotation_id
        self.save_project()
        self._refresh_annotation_list()
        self.canvas.update()

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
            self.canvas.selected_annotation_id = None
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()

    def auto_annotate(self):
        if not self.store.images:
            QMessageBox.information(self, APP_NAME, "Open a dataset first.")
            return
        dialog = AutoLabelDialog(self, default_scope="current")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_autolabel_dialog(dialog)

    def auto_label_current(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, APP_NAME, "Open a dataset and select an image first.")
            return
        dialog = AutoLabelDialog(self, default_scope="current")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.scope.setCurrentIndex(0)
            self._apply_autolabel_dialog(dialog)

    def auto_label_full_dataset(self):
        if not self.store.images:
            QMessageBox.information(self, APP_NAME, "Open a dataset first.")
            return
        dialog = AutoLabelDialog(self, default_scope="dataset")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.scope.setCurrentIndex(1)
            self._apply_autolabel_dialog(dialog)

    def _apply_autolabel_dialog(self, dialog: AutoLabelDialog):
        settings = dialog.settings()
        mapping = dialog.class_mapping()
        seg_options = dialog.segmentation_options()
        saved_defaults = dialog.remember_defaults()
        self.store.project.settings.setdefault("model_defaults", {}).update(saved_defaults)
        self.store.project.settings["last_autolabel_mapping"] = dialog.mapping_text.toPlainText()
        indices = [self.current_image_index] if dialog.selected_scope() == "current" else list(range(len(self.store.images)))
        indices = [i for i in indices if i >= 0]
        self._run_yolo_on_indices(indices, settings, mapping, seg_options)

    def _build_sam_segmenter(self, seg_options):
        if not seg_options.get("enabled"):
            return None
        checkpoint = seg_options.get("checkpoint_path") or self.store.project.settings.get("model_defaults", {}).get("default_segmentation_model", "")
        if not checkpoint:
            raise FileNotFoundError("Select a SAM checkpoint first, or set a default segmentation model.")
        return SamSegmenter(SamSettings(checkpoint, seg_options.get("model_type", "auto"), seg_options.get("device", "auto")))

    def _apply_segmentation_to_annotation(self, segmenter, image_path, annotation):
        mask = segmenter.segment_from_box(image_path, annotation.bbox)
        polygons = mask_to_polygons(mask)
        if polygons:
            # Use largest polygon by number of points. Good enough for v1.1.0.
            annotation.polygon = max(polygons, key=len)
            annotation.annotation_type = "polygon"
            annotation.source = "yolo+sam" if annotation.source == "yolo" else annotation.source + "+sam"
            annotation.touch()

    def _run_yolo_on_indices(self, indices, settings, class_mapping=None, seg_options=None):
        try:
            class_mapping = class_mapping or {}
            lookup = {c["name"]: int(c["id"]) for c in self.store.project.classes}
            labeler = YoloAutoLabeler(settings, class_mapping=class_mapping)
            segmenter = None
            if seg_options and seg_options.get("enabled"):
                try:
                    segmenter = self._build_sam_segmenter(seg_options)
                except Exception as exc:
                    if not seg_options.get("continue_if_fails", True):
                        raise
                    QMessageBox.warning(self, APP_NAME, f"Segmentation is unavailable. Continuing with YOLO boxes only.\n\n{exc}")
                    segmenter = None

            progress = QProgressDialog("Running auto annotation...", "Cancel", 0, len(indices), self)
            progress.setMinimumWidth(520)
            total = 0
            for step, index in enumerate(indices, 1):
                if progress.wasCanceled():
                    break
                image = self.store.images[index]
                image_path = Path(self.store.project.dataset_path) / image.relative_path
                annotations = labeler.predict_image(image_path, lookup)
                for annotation in annotations:
                    class_id = self.store.add_class(annotation.class_name)
                    annotation.class_id = class_id
                    if segmenter is not None and annotation.bbox:
                        try:
                            self._apply_segmentation_to_annotation(segmenter, image_path, annotation)
                        except Exception as exc:
                            if not seg_options.get("continue_if_fails", True):
                                raise
                            if not self._sam_warning_shown:
                                QMessageBox.warning(self, APP_NAME, f"SAM failed on one or more boxes. Continuing with YOLO boxes only.\n\n{exc}")
                                self._sam_warning_shown = True
                    self.store.add_annotation(index, annotation)
                total += len(annotations)
                progress.setValue(step)
            self.class_panel.set_classes([c["name"] for c in self.store.project.classes])
            self._refresh_class_colors()
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()
            self._status(f"Auto annotation added {total} predictions")
        except MissingYoloDependency as exc:
            QMessageBox.information(self, APP_NAME, str(exc))
        except MissingSegmentationDependency as exc:
            QMessageBox.information(self, APP_NAME, str(exc))
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Auto annotation failed.\n\n{exc}")

    def generate_mask_for_selected_bbox(self):
        annotation = self._selected_annotation()
        if not annotation or not annotation.bbox:
            QMessageBox.information(self, APP_NAME, "Select a bounding box first.")
            return
        defaults = self.store.project.settings.get("model_defaults", {})
        checkpoint = defaults.get("default_segmentation_model", "")
        if not checkpoint:
            QMessageBox.information(self, APP_NAME, "No default SAM model set. Open Auto Annotate → Segmentation and set a default SAM checkpoint.")
            return
        try:
            image = self.store.images[self.current_image_index]
            image_path = Path(self.store.project.dataset_path) / image.relative_path
            segmenter = SamSegmenter(SamSettings(checkpoint, defaults.get("default_sam_model_type", "auto"), defaults.get("default_device", "auto")))
            self._apply_segmentation_to_annotation(segmenter, image_path, annotation)
            self.save_project()
            self._refresh_annotation_list()
            self.canvas.update()
            self._status("Generated segmentation mask from selected box")
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Segmentation failed.\n\n{exc}")

    def _toggle_masks(self, value):
        self.canvas.show_masks = value
        self.canvas.update()

    def _set_mask_opacity(self, value):
        self.canvas.mask_opacity = value
        self.canvas.update()

    def analyze_dataset(self):
        self.insights.set_summary(analyze_project(self.store.project))
        self._status("Dataset analysis complete")

    def _perform_export(self, options):
        if not options or not options.get("output"):
            return
        output = Path(options["output"])
        fmt = options["format"]
        accepted_only = options.get("accepted_only", True)
        if fmt == "YOLO TXT":
            export_yolo(self.store.project, output / "yolo", accepted_only)
        elif fmt == "Pascal VOC XML":
            export_voc(self.store.project, output / "voc", accepted_only)
        elif fmt == "COCO Detection JSON":
            export_coco(self.store.project, output / "coco_detection.json", False, accepted_only)
        elif fmt == "COCO Segmentation JSON":
            export_coco(self.store.project, output / "coco_segmentation.json", True, accepted_only)
        elif fmt == "CSV Summary":
            export_csv_summary(self.store.project, output / "annotation_summary.csv", accepted_only)
        elif fmt == "Grouped YOLO":
            export_grouped(self.store.project, output, "yolo")
        else:
            raise ValueError(f"Unknown export format: {fmt}")
        self.store.project.settings["last_export_options"] = options
        self.save_project()
        QMessageBox.information(self, APP_NAME, f"Export complete:\n{output}")

    def export_dataset(self):
        dialog = ExportDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._perform_export(dialog.options())
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Export failed.\n\n{exc}")

    def quick_export(self):
        options = self.store.project.settings.get("last_export_options")
        if not options:
            QMessageBox.information(self, APP_NAME, "No previous export settings found. Use Export once first.")
            return
        try:
            self._perform_export(options)
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"Quick export failed.\n\n{exc}")

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
            try:
                augment_project(self.store.project, **dialog.options())
                QMessageBox.information(self, APP_NAME, "Augmentation complete. Check the selected output folder.")
            except Exception as exc:
                QMessageBox.warning(self, APP_NAME, f"Augmentation failed.\n\n{exc}")

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
