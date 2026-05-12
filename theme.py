import os
import logging
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

# Blender-inspired low-saturation palette
COLORS = {
    "window_bg": "#3D3D3D",
    "panel_bg": "#4A4A4A",
    "widget_bg": "#575757",
    "widget_hover": "#636363",
    "widget_pressed": "#4E4E4E",
    "input_bg": "#464646",
    "border": "#555555",
    "text_primary": "#D3D3D3",
    "text_secondary": "#888888",
    "accent": "#5C9BD5",
    "success": "#6BAF6D",
    "warning": "#B5A36A",
    "danger": "#B56A6A",
}


def load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "blender.qss")
    if not os.path.exists(qss_path):
        logger.warning("QSS stylesheet not found: %s", qss_path)
        return
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except OSError as e:
        logger.error("Failed to load stylesheet: %s", e)
