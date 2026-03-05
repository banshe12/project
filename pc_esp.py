import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

class ESPOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RF4 ESP Overlay")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Initial data
        self.fish_name = "Waiting..."
        self.weight = 0.0
        self.tension = 0
        self.distance = 0.0
        self.rod_tip_pos = QRect(0, 0, 0, 0)

        self.showFullScreen()

    def update_data(self, fish_name, weight, tension, distance, rod_tip_rect=None):
        self.fish_name = fish_name
        self.weight = weight
        self.tension = tension
        self.distance = distance
        if rod_tip_rect:
            self.rod_tip_pos = rod_tip_rect
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Rod Tip Bounding Box
        if self.rod_tip_pos.width() > 0:
            pen = QPen(QColor(0, 255, 0), 2)
            painter.setPen(pen)
            painter.drawRect(self.rod_tip_pos)

        # Draw Data Text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        info_text = (
            f"Fish: {self.fish_name}\n"
            f"Weight: {self.weight:.2f} kg\n"
            f"Tension: {self.tension}%\n"
            f"Distance: {self.distance:.2f}m"
        )

        # Position text
        if self.rod_tip_pos.width() > 0:
            text_rect = QRect(self.rod_tip_pos.right() + 10, self.rod_tip_pos.top(), 250, 120)
        else:
            text_rect = QRect(50, 50, 250, 120)

        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, info_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ESPOverlay()
    overlay.show()
    sys.exit(app.exec())
