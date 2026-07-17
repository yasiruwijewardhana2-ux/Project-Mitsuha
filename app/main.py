import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.ui.window import MainWindow
from app.robot.companion_core import CompanionCore

if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(level=logging.INFO)

    # UI scaling සැකසුම්
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)

    # Mitsuha ගේ Core එක init කරනවා
    core = CompanionCore()

    # MainWindow එකට core එක අරන් යනවා (ඔයාගේ window.py එකේ මේක දාගන්න)
    window = MainWindow(core) 
    window.show()

    sys.exit(app.exec())
