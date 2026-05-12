from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                              QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint


class TitleBar(QWidget):
    """Custom title bar with drag support and window control buttons."""

    about_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(4)

        self.title_label = QLabel("RTX 视频超分辨率工具")
        self.title_label.setStyleSheet("font-weight: bold; color: #D3D3D3; font-size: 13px;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.btn_about = _TitleButton("ⓘ")
        self.btn_about.clicked.connect(self.about_requested.emit)
        layout.addWidget(self.btn_about)

        self.btn_min = _TitleButton("─")
        self.btn_min.clicked.connect(self._on_minimize)
        self.btn_max = _TitleButton("□")
        self.btn_max.clicked.connect(self._on_maximize)
        self.btn_close = _TitleButton("✕")
        self.btn_close.clicked.connect(self._on_close)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def _on_minimize(self):
        w = self.window()
        if w:
            w.showMinimized()

    def _on_maximize(self):
        w = self.window()
        if w:
            if w.isMaximized():
                w.showNormal()
                self.btn_max.setText("□")
            else:
                w.showMaximized()
                self.btn_max.setText("❐")

    def _on_close(self):
        w = self.window()
        if w:
            w.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            w = self.window()
            if w and not w.isMaximized():
                delta = event.globalPosition().toPoint() - self._drag_pos
                w.move(w.x() + delta.x(), w.y() + delta.y())
                self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self._on_maximize()
        super().mouseDoubleClickEvent(event)


class _TitleButton(QPushButton):
    """Individual title bar button (minimize/maximize/close)."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(46, 32)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setObjectName("titleBarBtn")
