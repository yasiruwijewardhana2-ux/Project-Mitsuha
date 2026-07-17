import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.ui.window import MainWindow
from app.robot.companion_core import CompanionCore
from app.robot.voice_handler import VoiceThread

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)

    # Initialize Core & Voice
    core = CompanionCore()
    voice_thread = VoiceThread(core)
    
    window = MainWindow()
    window.show()

    # Voice Thread එක පටන් ගන්න
    voice_thread.start()

    # App එක Close වෙද්දී Thread එක නතර කරන්න
    app.aboutToQuit.connect(voice_thread.terminate)

    sys.exit(app.exec())
