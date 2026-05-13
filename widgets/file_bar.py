from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                              QLineEdit, QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropLineEdit(QLineEdit):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText("拖拽视频文件到此处，或点击右侧按钮选择")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("QLineEdit { border-color: #6BAF6D; }")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.setText(path)
            self.file_dropped.emit(path)


class FileBar(QWidget):
    input_changed = pyqtSignal(str)
    output_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        input_row = QHBoxLayout()
        input_label = QLabel("输入:")
        input_label.setFixedWidth(50)
        self.input_edit = DropLineEdit()
        self.input_edit.textChanged.connect(self._on_input_text_changed)
        self.input_edit.file_dropped.connect(self._on_input_text_changed)
        self.btn_input = QPushButton("选择文件")
        self.btn_input.clicked.connect(self._pick_input)
        input_row.addWidget(input_label)
        input_row.addWidget(self.input_edit, 1)
        input_row.addWidget(self.btn_input)

        output_row = QHBoxLayout()
        output_label = QLabel("输出:")
        output_label.setFixedWidth(50)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("留空则使用视频所在目录")
        self.btn_output = QPushButton("选择目录")
        self.btn_output.clicked.connect(self._pick_output)
        output_row.addWidget(output_label)
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(self.btn_output)

        layout.addLayout(input_row)
        layout.addLayout(output_row)

    def _on_input_text_changed(self, text=None):
        self.input_changed.emit(self.input_edit.text())

    def _pick_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv);;所有文件 (*.*)"
        )
        if path:
            self.input_edit.setText(path)

    def _pick_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_edit.setText(path)

    def get_input_path(self) -> str:
        return self.input_edit.text()

    def get_output_path(self) -> str:
        return self.output_edit.text()

    def set_output_path(self, path: str):
        self.output_edit.setText(path)
