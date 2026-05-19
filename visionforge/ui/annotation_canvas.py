from pathlib import Path
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from visionforge.core.bbox_utils import clamp_bbox


class AnnotationCanvas(QWidget):
    annotationCreated = Signal(list)
    annotationSelected = Signal(str)
    annotationChanged = Signal(str, list)
    deleteSelected = Signal(str)

    HANDLE_SIZE = 8
    MIN_BOX_SIZE = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.image_path = None
        self.image_record = None
        self.pixmap = None
        self.scale = 1
        self.offset_x = 0
        self.offset_y = 0
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        self.selected_annotation_id = None
        self.show_masks = True
        self.mask_opacity = .35

        self.interaction_mode = None  # draw / move / resize
        self.active_handle = None
        self.drag_start_img = None
        self.original_bbox = None
        self.active_annotation_id = None

    def load_image(self, path, record):
        self.image_path = Path(path)
        self.image_record = record
        self.pixmap = QPixmap(str(path)) if Path(path).exists() else None
        self.selected_annotation_id = None
        self._reset_interaction()
        self.update()

    def clear(self):
        self.image_path = None
        self.image_record = None
        self.pixmap = None
        self.selected_annotation_id = None
        self._reset_interaction()
        self.update()

    def _reset_interaction(self):
        self.drawing = False
        self.start_pos = None
        self.current_pos = None
        self.interaction_mode = None
        self.active_handle = None
        self.drag_start_img = None
        self.original_bbox = None
        self.active_annotation_id = None

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

    def _annotation_by_id(self, annotation_id):
        if not self.image_record:
            return None
        return next((a for a in self.image_record.annotations if a.annotation_id == annotation_id), None)

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
            if ann.polygon and self.show_masks:
                pts = [self.image_to_widget(x, y) for x, y in ann.polygon]
                qp.setPen(QPen(QColor("#22C55E"), 2))
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    qp.drawLine(a, b)
            if ann.bbox:
                x1, y1, x2, y2 = ann.bbox
                p1 = self.image_to_widget(x1, y1)
                p2 = self.image_to_widget(x2, y2)
                is_selected = ann.annotation_id == self.selected_annotation_id
                color = QColor("#FACC15") if is_selected else QColor("#38BDF8")
                if ann.status == "pending":
                    color = QColor("#FB923C")

                qp.setPen(QPen(color, 2))
                rect = QRect(p1, p2).normalized()
                qp.drawRect(rect)

                label = ann.class_name + (f" {ann.confidence:.2f}" if ann.confidence is not None else "")
                qp.fillRect(rect.x(), rect.y() - 18, max(80, len(label) * 7), 18, QColor(15, 23, 42, 210))
                qp.setPen(QColor("#F9FAFB"))
                qp.drawText(rect.x() + 4, rect.y() - 5, label)

                if is_selected:
                    self._draw_handles(qp, rect)

        if self.drawing and self.start_pos and self.current_pos:
            qp.setPen(QPen(QColor("#FFFFFF"), 2, Qt.DashLine))
            qp.drawRect(QRect(self.start_pos, self.current_pos).normalized())

    def _draw_handles(self, qp, rect):
        qp.setPen(QPen(QColor("#111827"), 1))
        qp.setBrush(QColor("#FACC15"))
        for handle_rect in self._handle_rects(rect).values():
            qp.drawRect(handle_rect)
        qp.setBrush(Qt.NoBrush)

    def _handle_rects(self, rect):
        s = self.HANDLE_SIZE
        hs = s // 2
        cx = rect.center().x()
        cy = rect.center().y()
        points = {
            "tl": QPoint(rect.left(), rect.top()),
            "tc": QPoint(cx, rect.top()),
            "tr": QPoint(rect.right(), rect.top()),
            "rc": QPoint(rect.right(), cy),
            "br": QPoint(rect.right(), rect.bottom()),
            "bc": QPoint(cx, rect.bottom()),
            "bl": QPoint(rect.left(), rect.bottom()),
            "lc": QPoint(rect.left(), cy),
        }
        return {name: QRect(p.x() - hs, p.y() - hs, s, s) for name, p in points.items()}

    def _bbox_rect(self, ann):
        x1, y1, x2, y2 = ann.bbox
        return QRect(self.image_to_widget(x1, y1), self.image_to_widget(x2, y2)).normalized()

    def _handle_hit(self, pos, ann):
        if not ann or not ann.bbox:
            return None
        for name, rect in self._handle_rects(self._bbox_rect(ann)).items():
            if rect.contains(pos):
                return name
        return None

    def _hit(self, pos):
        if not self.image_record:
            return None
        ix, iy = self.widget_to_image(pos)
        for ann in reversed(self.image_record.annotations):
            if ann.bbox and ann.status != "rejected":
                x1, y1, x2, y2 = ann.bbox
                if x1 <= ix <= x2 and y1 <= iy <= y2:
                    return ann
        return None

    def _image_bounds_contains(self, pos):
        return self._rect().contains(pos)

    def mousePressEvent(self, event: QMouseEvent):
        self.setFocus()
        if event.button() != Qt.LeftButton or not self.pixmap or not self.image_record:
            return

        p = event.position().toPoint()
        if not self._image_bounds_contains(p):
            return

        selected_ann = self._annotation_by_id(self.selected_annotation_id)
        handle = self._handle_hit(p, selected_ann)
        if handle:
            self.interaction_mode = "resize"
            self.active_handle = handle
            self.active_annotation_id = selected_ann.annotation_id
            self.original_bbox = list(selected_ann.bbox)
            self.drag_start_img = self.widget_to_image(p)
            return

        ann = self._hit(p)
        if ann:
            self.selected_annotation_id = ann.annotation_id
            self.annotationSelected.emit(ann.annotation_id)
            self.interaction_mode = "move"
            self.active_annotation_id = ann.annotation_id
            self.original_bbox = list(ann.bbox)
            self.drag_start_img = self.widget_to_image(p)
            self.update()
            return

        self.drawing = True
        self.interaction_mode = "draw"
        self.start_pos = p
        self.current_pos = p

    def mouseMoveEvent(self, event):
        if not self.pixmap or not self.image_record:
            return
        p = event.position().toPoint()

        if self.interaction_mode == "draw" and self.drawing:
            self.current_pos = p
            self.update()
            return

        if self.interaction_mode in ("move", "resize"):
            ann = self._annotation_by_id(self.active_annotation_id)
            if not ann or not self.original_bbox or not self.drag_start_img:
                return
            ix, iy = self.widget_to_image(p)
            sx, sy = self.drag_start_img
            dx, dy = ix - sx, iy - sy
            if self.interaction_mode == "move":
                x1, y1, x2, y2 = self.original_bbox
                w, h = x2 - x1, y2 - y1
                nx1, ny1 = x1 + dx, y1 + dy
                nx2, ny2 = nx1 + w, ny1 + h
                if nx1 < 0:
                    nx2 -= nx1
                    nx1 = 0
                if ny1 < 0:
                    ny2 -= ny1
                    ny1 = 0
                if nx2 > self.image_record.width:
                    nx1 -= (nx2 - self.image_record.width)
                    nx2 = self.image_record.width
                if ny2 > self.image_record.height:
                    ny1 -= (ny2 - self.image_record.height)
                    ny2 = self.image_record.height
                ann.bbox = clamp_bbox([nx1, ny1, nx2, ny2], self.image_record.width, self.image_record.height)
            else:
                ann.bbox = self._resize_bbox(self.original_bbox, dx, dy, self.active_handle)
            self.update()
            return

        selected_ann = self._annotation_by_id(self.selected_annotation_id)
        handle = self._handle_hit(p, selected_ann)
        if handle:
            self.setCursor(self._cursor_for_handle(handle))
        elif self._hit(p):
            self.setCursor(QCursor(Qt.SizeAllCursor))
        else:
            self.setCursor(QCursor(Qt.CrossCursor))

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not self.image_record:
            return

        if self.interaction_mode == "draw" and self.drawing and self.start_pos:
            self.drawing = False
            end = event.position().toPoint()
            x1, y1 = self.widget_to_image(self.start_pos)
            x2, y2 = self.widget_to_image(end)
            bbox = clamp_bbox([x1, y1, x2, y2], self.image_record.width, self.image_record.height)
            self._reset_interaction()
            if abs(bbox[2] - bbox[0]) >= self.MIN_BOX_SIZE and abs(bbox[3] - bbox[1]) >= self.MIN_BOX_SIZE:
                self.annotationCreated.emit(bbox)
            self.update()
            return

        if self.interaction_mode in ("move", "resize") and self.active_annotation_id:
            ann = self._annotation_by_id(self.active_annotation_id)
            changed_id = self.active_annotation_id
            changed_bbox = list(ann.bbox) if ann and ann.bbox else None
            self._reset_interaction()
            if ann and changed_bbox:
                self.annotationChanged.emit(changed_id, changed_bbox)
            self.update()
            return

        self._reset_interaction()
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace) and self.selected_annotation_id:
            self.deleteSelected.emit(self.selected_annotation_id)
            event.accept()
            return
        super().keyPressEvent(event)

    def _resize_bbox(self, bbox, dx, dy, handle):
        x1, y1, x2, y2 = bbox
        if "l" in handle:
            x1 += dx
        if "r" in handle:
            x2 += dx
        if "t" in handle:
            y1 += dy
        if "b" in handle:
            y2 += dy
        out = clamp_bbox([x1, y1, x2, y2], self.image_record.width, self.image_record.height)
        if abs(out[2] - out[0]) < self.MIN_BOX_SIZE or abs(out[3] - out[1]) < self.MIN_BOX_SIZE:
            return list(bbox)
        return out

    def _cursor_for_handle(self, handle):
        if handle in ("tl", "br"):
            return QCursor(Qt.SizeFDiagCursor)
        if handle in ("tr", "bl"):
            return QCursor(Qt.SizeBDiagCursor)
        if handle in ("lc", "rc"):
            return QCursor(Qt.SizeHorCursor)
        return QCursor(Qt.SizeVerCursor)
