from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from visionforge.core.bbox_utils import clamp_bbox


class AnnotationCanvas(QWidget):
    annotationCreated = Signal(list)
    annotationSelected = Signal(str)
    annotationChanged = Signal(str)
    deleteRequested = Signal()

    HANDLE_SIZE = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.image_path = None
        self.image_record = None
        self.pixmap = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drawing = False
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.start_pos = None
        self.current_pos = None
        self.drag_start_img = None
        self.original_bbox = None
        self.selected_annotation_id = None
        self.show_masks = True
        self.mask_opacity = 0.35
        self.class_colors = {}

    def set_class_colors(self, colors):
        self.class_colors = dict(colors or {})
        self.update()

    def load_image(self, path, record):
        self.image_path = Path(path)
        self.image_record = record
        self.pixmap = QPixmap(str(path)) if Path(path).exists() else None
        self.selected_annotation_id = None
        self.update()

    def clear(self):
        self.image_path = None
        self.image_record = None
        self.pixmap = None
        self.selected_annotation_id = None
        self.update()

    def _rect(self):
        if not self.pixmap:
            return QRect()
        self.scale = min(max(1, self.width() - 20) / self.pixmap.width(), max(1, self.height() - 20) / self.pixmap.height())
        w = int(self.pixmap.width() * self.scale)
        h = int(self.pixmap.height() * self.scale)
        self.offset_x = (self.width() - w) // 2
        self.offset_y = (self.height() - h) // 2
        return QRect(self.offset_x, self.offset_y, w, h)

    def image_to_widget(self, x, y):
        return QPoint(int(self.offset_x + x * self.scale), int(self.offset_y + y * self.scale))

    def widget_to_image(self, p):
        return ((p.x() - self.offset_x) / self.scale, (p.y() - self.offset_y) / self.scale)

    def _annotation_color(self, ann):
        if ann.status == "pending":
            return QColor("#FB923C")
        if ann.annotation_id == self.selected_annotation_id:
            return QColor("#FACC15")
        return QColor(self.class_colors.get(ann.class_name, "#38BDF8"))

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), QColor("#0B1120"))
        if not self.pixmap or not self.image_record:
            qp.setPen(QColor("#9CA3AF"))
            qp.drawText(self.rect(), Qt.AlignCenter, "Open a dataset to start annotating")
            return

        qp.drawPixmap(self._rect(), self.pixmap)

        for ann in self.image_record.annotations:
            if ann.status == "rejected":
                continue
            color = self._annotation_color(ann)
            if ann.polygon and self.show_masks:
                pts = [self.image_to_widget(x, y) for x, y in ann.polygon]
                qp.setPen(QPen(color, 2))
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    qp.drawLine(a, b)
            if ann.bbox:
                x1, y1, x2, y2 = ann.bbox
                p1 = self.image_to_widget(x1, y1)
                p2 = self.image_to_widget(x2, y2)
                qp.setPen(QPen(color, 2))
                qp.drawRect(QRect(p1, p2))
                label = ann.class_name + (f" {ann.confidence:.2f}" if ann.confidence is not None else "")
                qp.fillRect(p1.x(), p1.y() - 18, max(80, len(label) * 7), 18, QColor(15, 23, 42, 220))
                qp.setPen(QColor("#F9FAFB"))
                qp.drawText(p1.x() + 4, p1.y() - 5, label)

                if ann.annotation_id == self.selected_annotation_id:
                    qp.setPen(QPen(QColor("#FACC15"), 1))
                    qp.setBrush(QColor("#111827"))
                    for r in self._handle_rects(ann).values():
                        qp.drawRect(r)
                    qp.setBrush(Qt.NoBrush)

        if self.drawing and self.start_pos and self.current_pos:
            qp.setPen(QPen(QColor("#FFFFFF"), 2, Qt.DashLine))
            qp.drawRect(QRect(self.start_pos, self.current_pos))

    def _selected_annotation(self):
        if not self.image_record or not self.selected_annotation_id:
            return None
        return next((a for a in self.image_record.annotations if a.annotation_id == self.selected_annotation_id), None)

    def _handle_rects(self, ann):
        if not ann.bbox:
            return {}
        x1, y1, x2, y2 = ann.bbox
        pts = {
            "tl": self.image_to_widget(x1, y1), "tr": self.image_to_widget(x2, y1),
            "bl": self.image_to_widget(x1, y2), "br": self.image_to_widget(x2, y2),
            "l": self.image_to_widget(x1, (y1 + y2) / 2), "r": self.image_to_widget(x2, (y1 + y2) / 2),
            "t": self.image_to_widget((x1 + x2) / 2, y1), "b": self.image_to_widget((x1 + x2) / 2, y2),
        }
        half = self.HANDLE_SIZE // 2
        return {k: QRect(p.x() - half, p.y() - half, self.HANDLE_SIZE, self.HANDLE_SIZE) for k, p in pts.items()}

    def _hit_handle(self, pos):
        ann = self._selected_annotation()
        if not ann:
            return None
        for name, rect in self._handle_rects(ann).items():
            if rect.contains(pos):
                return name
        return None

    def _hit(self, pos):
        ix, iy = self.widget_to_image(pos)
        for ann in reversed(self.image_record.annotations if self.image_record else []):
            if ann.bbox and ann.status != "rejected":
                x1, y1, x2, y2 = ann.bbox
                if x1 <= ix <= x2 and y1 <= iy <= y2:
                    return ann
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.LeftButton or not self.pixmap or not self.image_record:
            return
        self.setFocus()
        p = event.position().toPoint()
        handle = self._hit_handle(p)
        if handle:
            self.resizing = True
            self.resize_handle = handle
            self.start_pos = p
            ann = self._selected_annotation()
            self.original_bbox = list(ann.bbox) if ann and ann.bbox else None
            return
        ann = self._hit(p)
        if ann:
            self.selected_annotation_id = ann.annotation_id
            self.annotationSelected.emit(ann.annotation_id)
            self.dragging = True
            self.drag_start_img = self.widget_to_image(p)
            self.original_bbox = list(ann.bbox) if ann.bbox else None
            self.update()
            return
        self.drawing = True
        self.start_pos = p
        self.current_pos = p

    def mouseMoveEvent(self, event):
        p = event.position().toPoint()
        if self.drawing:
            self.current_pos = p
            self.update()
            return
        ann = self._selected_annotation()
        if not ann or not self.original_bbox:
            return
        if self.dragging:
            sx, sy = self.drag_start_img
            cx, cy = self.widget_to_image(p)
            dx, dy = cx - sx, cy - sy
            x1, y1, x2, y2 = self.original_bbox
            w, h = x2 - x1, y2 - y1
            nx1 = max(0, min(self.image_record.width - w, x1 + dx))
            ny1 = max(0, min(self.image_record.height - h, y1 + dy))
            ann.bbox = [nx1, ny1, nx1 + w, ny1 + h]
            ann.touch()
            self.update()
        elif self.resizing:
            ix, iy = self.widget_to_image(p)
            x1, y1, x2, y2 = self.original_bbox
            h = self.resize_handle
            if "l" in h:
                x1 = ix
            if "r" in h:
                x2 = ix
            if "t" in h:
                y1 = iy
            if "b" in h:
                y2 = iy
            ann.bbox = clamp_bbox([x1, y1, x2, y2], self.image_record.width, self.image_record.height)
            ann.touch()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self.dragging or self.resizing:
            ann = self._selected_annotation()
            if ann:
                self.annotationChanged.emit(ann.annotation_id)
            self.dragging = False
            self.resizing = False
            self.resize_handle = None
            self.original_bbox = None
            self.update()
            return
        if not self.drawing or not self.start_pos or not self.image_record:
            return
        self.drawing = False
        end = event.position().toPoint()
        x1, y1 = self.widget_to_image(self.start_pos)
        x2, y2 = self.widget_to_image(end)
        bbox = clamp_bbox([x1, y1, x2, y2], self.image_record.width, self.image_record.height)
        if abs(bbox[2] - bbox[0]) >= 5 and abs(bbox[3] - bbox[1]) >= 5:
            self.annotationCreated.emit(bbox)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.deleteRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)
