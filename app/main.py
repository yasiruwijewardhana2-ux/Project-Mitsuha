import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.ui.window import MainWindow
from app.robot.companion_core import CompanionCore

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)

    # Core එක විතරයි දැන් තියෙන්නේ
    core = CompanionCore()
    
    # Window එකට core එක දෙනවා
    window = MainWindow(core)
    window.show()

    sys.exit(app.exec())
