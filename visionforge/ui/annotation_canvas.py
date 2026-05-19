from pathlib import Path
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from visionforge.core.bbox_utils import clamp_bbox

class AnnotationCanvas(QWidget):
    annotationCreated=Signal(list); annotationSelected=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent); self.setMinimumSize(640,480); self.setMouseTracking(True); self.image_path=None; self.image_record=None; self.pixmap=None; self.scale=1; self.offset_x=0; self.offset_y=0; self.drawing=False; self.start_pos=None; self.current_pos=None; self.selected_annotation_id=None; self.show_masks=True; self.mask_opacity=.35
    def load_image(self,path,record):
        self.image_path=Path(path); self.image_record=record; self.pixmap=QPixmap(str(path)) if Path(path).exists() else None; self.selected_annotation_id=None; self.update()
    def clear(self): self.image_path=None; self.image_record=None; self.pixmap=None; self.update()
    def _rect(self):
        if not self.pixmap: return QRect()
        self.scale=min(max(1,self.width()-20)/self.pixmap.width(), max(1,self.height()-20)/self.pixmap.height()); w=int(self.pixmap.width()*self.scale); h=int(self.pixmap.height()*self.scale); self.offset_x=(self.width()-w)//2; self.offset_y=(self.height()-h)//2; return QRect(self.offset_x,self.offset_y,w,h)
    def image_to_widget(self,x,y): return QPoint(int(self.offset_x+x*self.scale), int(self.offset_y+y*self.scale))
    def widget_to_image(self,p): return ((p.x()-self.offset_x)/self.scale, (p.y()-self.offset_y)/self.scale)
    def paintEvent(self,event):
        qp=QPainter(self); qp.fillRect(self.rect(), QColor('#0B1120'))
        if not self.pixmap or not self.image_record:
            qp.setPen(QColor('#9CA3AF')); qp.drawText(self.rect(), Qt.AlignCenter, 'Open a dataset to start annotating'); return
        qp.drawPixmap(self._rect(), self.pixmap)
        for ann in self.image_record.annotations:
            if ann.status=='rejected': continue
            if ann.polygon and self.show_masks:
                pts=[self.image_to_widget(x,y) for x,y in ann.polygon]; qp.setPen(QPen(QColor('#22C55E'),2))
                for a,b in zip(pts, pts[1:]+pts[:1]): qp.drawLine(a,b)
            if ann.bbox:
                x1,y1,x2,y2=ann.bbox; p1=self.image_to_widget(x1,y1); p2=self.image_to_widget(x2,y2); color=QColor('#FACC15') if ann.annotation_id==self.selected_annotation_id else QColor('#38BDF8')
                if ann.status=='pending': color=QColor('#FB923C')
                qp.setPen(QPen(color,2)); qp.drawRect(QRect(p1,p2)); label=ann.class_name+(f' {ann.confidence:.2f}' if ann.confidence is not None else '')
                qp.fillRect(p1.x(), p1.y()-18, max(80,len(label)*7), 18, QColor(15,23,42,210)); qp.setPen(QColor('#F9FAFB')); qp.drawText(p1.x()+4,p1.y()-5,label)
        if self.drawing and self.start_pos and self.current_pos:
            qp.setPen(QPen(QColor('#FFFFFF'),2,Qt.DashLine)); qp.drawRect(QRect(self.start_pos,self.current_pos))
    def mousePressEvent(self,event: QMouseEvent):
        if event.button()!=Qt.LeftButton or not self.pixmap or not self.image_record: return
        p=event.position().toPoint(); ann=self._hit(p)
        if ann: self.selected_annotation_id=ann.annotation_id; self.annotationSelected.emit(ann.annotation_id); self.update(); return
        self.drawing=True; self.start_pos=p; self.current_pos=p
    def mouseMoveEvent(self,event):
        if self.drawing: self.current_pos=event.position().toPoint(); self.update()
    def mouseReleaseEvent(self,event):
        if event.button()!=Qt.LeftButton or not self.drawing or not self.start_pos or not self.image_record: return
        self.drawing=False; end=event.position().toPoint(); x1,y1=self.widget_to_image(self.start_pos); x2,y2=self.widget_to_image(end); bbox=clamp_bbox([x1,y1,x2,y2], self.image_record.width, self.image_record.height)
        if abs(bbox[2]-bbox[0])>=5 and abs(bbox[3]-bbox[1])>=5: self.annotationCreated.emit(bbox)
        self.update()
    def _hit(self,pos):
        ix,iy=self.widget_to_image(pos)
        for ann in reversed(self.image_record.annotations):
            if ann.bbox and ann.status!='rejected':
                x1,y1,x2,y2=ann.bbox
                if x1<=ix<=x2 and y1<=iy<=y2: return ann
        return None
