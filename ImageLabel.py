from PyQt5.QtCore import QRect, QSize, QPoint, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget, QApplication
from PyQt5.QtCore import Qt


class ImageLabel(QLabel):
    def __init__(self, selection_manager, parent=None):
        super().__init__(parent)
        self.selection_manager = selection_manager
        self.selection_manager.selection_changed.connect(self.update_selection)
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.dragging_corner = None
        self.resize_margin = 10  # Size of corner handles
        self.max_width = 400  # Maximum width for the selection rectangle
        self.max_height = 250  # Maximum height for the selection rectangle

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.dragging_corner = self.get_dragging_corner(pos)
            if self.dragging_corner is not None:
                # Start resizing from a corner
                self.start_point = None
            else:
                # Start drawing a new rectangle
                self.start_point = pos
                self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging_corner is not None:
            # Resize the rectangle
            if self.selection_rect:
                if self.dragging_corner == "top_left":
                    self.selection_rect.setTopLeft(self.clamp_point(event.pos(), self.selection_rect.bottomRight()))
                elif self.dragging_corner == "top_right":
                    self.selection_rect.setTopRight(self.clamp_point(event.pos(), self.selection_rect.bottomLeft()))
                elif self.dragging_corner == "bottom_left":
                    self.selection_rect.setBottomLeft(self.clamp_point(event.pos(), self.selection_rect.topRight()))
                elif self.dragging_corner == "bottom_right":
                    self.selection_rect.setBottomRight(self.clamp_point(event.pos(), self.selection_rect.topLeft()))
                self.selection_manager.set_selection(self.selection_rect.topLeft(), self.selection_rect.bottomRight())
        elif self.start_point is not None:
            # Update the rectangle during dragging
            self.end_point = self.clamp_point(event.pos(), self.start_point)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.dragging_corner is None and self.start_point:
                self.end_point = self.clamp_point(event.pos(), self.start_point)
                self.selection_rect = QRect(self.start_point, self.end_point).normalized()
                self.selection_manager.set_selection(self.start_point, self.end_point)
            self.dragging_corner = None
        self.update()

    def paintEvent(self, event):
        # Draw the image and the rectangle with corner handles
        super().paintEvent(event)
        if self.selection_rect:
            painter = QPainter(self)
            # Draw the rectangle
            pen = QPen(QColor("blue"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)

            # Draw the resizing corners
            corner_color = QColor("red")
            painter.setBrush(corner_color)
            for corner in self.get_corners(self.selection_rect):
                painter.drawRect(corner)

    def get_corners(self, rect):
        # Returns the corner rectangles for resizing
        size = self.resize_margin
        return [
            QRect(rect.topLeft(), QSize(size, size)),  # Top-left corner
            QRect(rect.topRight() - QPoint(size, 0), QSize(size, size)),  # Top-right corner
            QRect(rect.bottomLeft() - QPoint(0, size), QSize(size, size)),  # Bottom-left corner
            QRect(rect.bottomRight() - QPoint(size, size), QSize(size, size)),  # Bottom-right corner
        ]

    def get_dragging_corner(self, pos):
        # Determine if the user is clicking near a corner
        if not self.selection_rect:
            return None
        corners = self.get_corners(self.selection_rect)
        if corners[0].contains(pos):
            return "top_left"
        elif corners[1].contains(pos):
            return "top_right"
        elif corners[2].contains(pos):
            return "bottom_left"
        elif corners[3].contains(pos):
            return "bottom_right"
        return None

    def update_selection(self, rect):
        # Update the selection rectangle from the manager
        self.selection_rect = rect
        self.update()

    def clamp_point(self, point, anchor_point):
        # Clamp the rectangle dimensions to the maximum size
        dx = min(max(point.x() - anchor_point.x(), -self.max_width), self.max_width)
        dy = min(max(point.y() - anchor_point.y(), -self.max_height), self.max_height)
        return QPoint(anchor_point.x() + dx, anchor_point.y() + dy)

class SelectionManager(QObject):
    selection_changed = pyqtSignal(QRect)  # Signal to notify when selection changes

    def __init__(self):
        super().__init__()
        self.start_point = None
        self.end_point = None

    def set_selection(self, start_point: QPoint, end_point: QPoint):
        self.start_point = start_point
        self.end_point = end_point
        rect = QRect(start_point, end_point).normalized()
        self.selection_changed.emit(rect)




class ScrollableLabel(QLabel):
    scrollDirectionChanged = pyqtSignal(str)  # Correctly declare the signal

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignTop)
        self.setWordWrap(True)
        self.setText(text)

    def wheelEvent(self, event):
        """Override the wheel event to detect scroll direction and emit signal."""
        angle = event.angleDelta().y()
        if angle > 0:
            scroll_direction = "down"
        elif angle < 0:
            scroll_direction = "up"
        else:
            scroll_direction = "none"

        # Emit the signal with the scroll direction
        self.scrollDirectionChanged.emit(scroll_direction)

        # Let the scroll area handle the event for scrolling
        super().wheelEvent(event)