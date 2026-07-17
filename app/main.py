import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt


class MitsuhaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Project Mitsuha")
        self.setFixedSize(320, 240)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Background
        painter.fillRect(self.rect(), QColor(15, 15, 15))

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)

        # Left Eye
        painter.drawEllipse(70, 80, 70, 70)

        # Right Eye
        painter.drawEllipse(180, 80, 70, 70)


app = QApplication(sys.argv)

window = MitsuhaWindow()
window.show()

sys.exit(app.exec())
