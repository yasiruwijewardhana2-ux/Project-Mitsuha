import sys
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.ui.window import MainWindow


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
